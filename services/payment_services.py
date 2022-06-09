import json
from services import firebase_services
from schemas import user_schemas, payment_schemas
from models import user_models, order_models, payment_models
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from fastapi import status, BackgroundTasks
import constants
import os
from dotenv import load_dotenv
from utility_services import common_services
try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
    from urllib.request import HTTPHandler, Request, build_opener
except ImportError:
    from urllib import urlencode

    from urllib2 import HTTPError, HTTPHandler, Request, URLError, build_opener

load_dotenv()


def checkout_id(user_request):

    url = "https://eu-test.oppwa.com/v1/checkouts"
    data = {
        'entityId': user_request['entityId'],
        'amount': user_request['amount'],
        'currency': user_request['currency'],
        'paymentType': user_request['paymentType']
    }
    if user_request['registrationId']:
        data['registrations[0].id'] = user_request['registrationId']
        data['standingInstruction.source'] = 'CIT'
        data['standingInstruction.mode'] = 'REPEATED'
        data['standingInstruction.type'] = 'UNSCHEDULED'
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=urlencode(data).encode('utf-8'))
        request.add_header(
            'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
        request.get_method = lambda: 'POST'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason


def get_payment_status(id, entityId=None):
    url = f"https://eu-test.oppwa.com/v1/checkouts/{id}/payment"
    url += f'?entityId={entityId}'
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=b'')
        request.add_header(
            'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
        request.get_method = lambda: 'GET'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason


def delete_card(id, entityId):
    url = f"https://eu-test.oppwa.com/v1/registrations/{id}"
    url += f'?entityId={entityId}'
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=b'')
        request.add_header(
            'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
        request.get_method = lambda: 'DELETE'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason


def get_payment_checkout_id(user_request, db: Session):
    
    customer_id = user_request.customer_id
    db_user_active = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()
    if db_user_active:
        if db_user_active.verification_status == "active":
            return checkout_id(user_request)
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order")
            return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Customer does't exist!")
        return common_msg


def get_payment_status_api(entityId, checkout_id, db: Session):
    
    return get_payment_status(checkout_id, entityId)


def get_all_banks(db: Session):
    
    bank_data = db.execute(
        f"select * from {constants.Database_name}.banks where status = True ; ")
    if bank_data.rowcount > 0:
        banks_list = []
        for data in bank_data:
            result = payment_schemas.BankResponse(title=data.title, bank_name=data.bank_name, account_name=data.account_name,
                                                  city=data.city, branch=data.branch, iban=data.iban)
            banks_list.append(result)
        response = payment_schemas.ResponseBankData(
            status=status.HTTP_200_OK, message="All banks list", data=banks_list)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Banks found")
        return common_msg


def upload_bank_payment_image(customer_id, order_id, image, db: Session):
    
    order_data = db.query(order_models.OrderTransactions).filter(
        order_models.OrderTransactions.order_id == order_id).first()
    if not order_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Order id not found")
        return common_msg

    path = os.path.abspath('.')

    image_path = os.path.join(path, 'common_folder')
    inner_image_path = os.path.join(image_path, 'customer_banks')
    filepath = image.filename
    extension = filepath.split(".")[-1]
    db_path = f"bank_payment_orderId-{order_id}."+extension
    stored_path = os.path.join(
        inner_image_path, db_path)

    if os.path.exists(stored_path):
        os.remove(stored_path)

    with open(os.path.join(stored_path), "wb+") as file_object:
        file_object.write(image.file.read())
        file_object.close()

    order_data.bank_payment_image = db_path
    db.merge(order_data)
    db.commit()
    prfl_path = user_schemas.UploadProfiledata(path=db_path)
    common_msg = user_schemas.UploadProfile(
        status=status.HTTP_200_OK, message="success", data=prfl_path)

    try:
        customer_data = db.execute(
            f"select * from {constants.Database_name}.customer_device where customer_id = {customer_id} and is_active=True ;")

        setting_message = db.execute(
            f"select * from {constants.Database_name}.settings where settings.key = 'bank_receipt_upload_notification' ;")

        order_ref_no = db.execute(
            f"select ref_number from {constants.Database_name}.orders where orders.id = {order_id} ;")

        for msg in setting_message:
            message = msg.value
            title_message = msg.display_name

        for ref_no in order_ref_no:
            ref = ref_no[0]
        values = {
            "order_ref_no": ref
        }

        message = message.format(**values)

        if customer_data:
            for data in customer_data:
                notf = user_schemas.PushNotificationFirebase(
                    title=title_message, message=message, device_token=data.device_id, order_id=order_id)
                firebase_services.push_notification_in_firebase(notf)

            if notf:
                fire = user_models.CustomerNotification(
                    customer_id=customer_id, order_id=order_id, title=notf.title, message=notf.message, created_at=common_services.get_time())
                db.merge(fire)
                db.commit()
    except Exception as e:
        print(e)
    return common_msg


def download_bank_payment_image(order_id, db: Session):
    
    path = os.path.abspath('.')

    image_path = os.path.join(path, 'common_folder')
    common_dir_path = os.path.join(image_path, 'customer_banks')
    order_data = db.query(order_models.OrderTransactions).filter(
        order_models.OrderTransactions.order_id == order_id).first()
    if not order_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Order id not found")
    file_name = order_data.bank_payment_image
    if file_name in os.listdir(common_dir_path):
        file_path = constants.BANK_PAYMENT_IMAGES_PATH + file_name
        data2 = user_schemas.Responsedocs(file_path=file_path)
        response = user_schemas.Responsedocspath(
            status=status.HTTP_200_OK, message='success', data=data2)
        return response
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file_name}")
    return common_msg


def get_customer_cards(customer_id, db: Session):
    
    user_cards = db.execute(
        f'select * from {constants.Database_name}.customer_cards where customer_id = "{customer_id}"')
    if user_cards:
        cards = []
        for card in user_cards:
            data = payment_schemas.ResponseCustomerCards(id=card.id, card_number=card.card_number, expiry_month=card.expiry_month, expiry_year=card.expiry_year,
                                                         card_holder=card.card_holder, card_type=card.card_type, card_brand=card.card_brand, card_id=card.registration_id)
            cards.append(data)
        response = payment_schemas.ResponseCustomerCardsFinal(
            status=status.HTTP_200_OK, message="User Cards!", data=cards)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No card found!")
        return common_msg


def delete_customer_card(card_id, entityId, db: Session):
    
    card = db.query(payment_models.CustomerCard).filter(
        payment_models.CustomerCard.registration_id == card_id).first()
    if not card:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Card Doesn't Exist!")
        return common_msg
    db.delete(card)
    db.commit()
    hyperpay = delete_card(card_id, entityId)
    print(hyperpay)
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Card Deleted Successfully!")
    return common_msg


def get_payment_types(db: Session):
    
    payment_types = db.execute(
        f'select * from {constants.Database_name}.status_master where status_type = 3 and status = 1')
    payment_type_list = []
    for data in payment_types:
        result = payment_schemas.ResponsePaymentsType(
            id=data.id, mode=data.name, status=data.status)
        payment_type_list.append(result)
    response = payment_schemas.ResponsePaymentsTypeFinal(
        status=status.HTTP_200_OK, message="User Cards!", data=payment_type_list)
    return response


def get_payment_status_types(db: Session):
    
    payment_status_types = db.execute(
        f'select * from {constants.Database_name}.status_master where status_type = 2')
    payment_status_list = []
    for data in payment_status_types:
        result = payment_schemas.ResponsePaymentstatus(
            id=data.id, payment_status_name=data.name, status=data.status)
        payment_status_list.append(result)
    response = payment_schemas.ResponsePaymentstatusFinal(
        status=status.HTTP_200_OK, message="all payments status type!", data=payment_status_list)
    return response
