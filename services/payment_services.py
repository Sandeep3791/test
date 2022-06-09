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
