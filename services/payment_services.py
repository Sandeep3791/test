import json

from sqlalchemy import desc
from services import firebase_services
from schemas import user_schemas, payment_schemas,order_schemas
from models import user_models, order_models, payment_models
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from fastapi import status, BackgroundTasks
import constants
import os ,re
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


class HyperPayResponseView:
    """
    Handle the response from HyperPay after processing the payment.
    The result codes returned by HyperPay are documented at https://hyperpay.docs.oppwa.com/reference/resultCodes
    """
    ENTITY_ID = None
    URL = "https://eu-test.oppwa.com/v1/"
    TOKEN = os.getenv('AUTHORIZATION_TOKEN')
    SUCCESS_CODES_REGEX = re.compile(r'^(000\.000\.|000\.100\.1|000\.[36])')
    SUCCESS_MANUAL_REVIEW_CODES_REGEX = re.compile(
        r'^(000\.400\.0[^3]|000\.400\.[0-1]{2}0)')
    PENDING_CHANGEABLE_SOON_CODES_REGEX = re.compile(r'^(000\.200)')
    PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX = re.compile(
        r'^(800\.400\.5|100\.400\.500)')

    def __init__(self, entityId):
        if entityId == 'hyper_VISA':
            self.ENTITY_ID = os.getenv('HYPER_VISA')
        elif entityId == 'hyper_MADA':
            self.ENTITY_ID = os.getenv('HYPER_MADA')
        elif entityId == 'hyper_MASTER':
            self.ENTITY_ID = os.getenv('HYPER_MASTER')

    def _verify_status(self, hyperpay_response):
        pending = False
        paid = False
        """
        Verify the status of the payment.
        """
        result_code = hyperpay_response['result']['code']
        if self.PENDING_CHANGEABLE_SOON_CODES_REGEX.search(result_code):
            pending = True
        elif self.PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX.search(result_code):
            pending = True
        elif self.SUCCESS_CODES_REGEX.search(result_code):
            paid = True
        elif self.SUCCESS_MANUAL_REVIEW_CODES_REGEX.search(result_code):
            paid = True
        else:
            pending, paid = False, False

        return pending, paid

    def generate_checkout_id(self, request):
        data = {
            'entityId': self.ENTITY_ID,
            'amount': request.get("amount"),
            'currency': request.get("currency"),
            'paymentType': request.get("paymentType")
        }
        if request.get("registrationId"):
            data['registrations[0].id'] = request.get("registrationId")
            data['standingInstruction.source'] = 'CIT'
            data['standingInstruction.mode'] = 'REPEATED'
            data['standingInstruction.type'] = 'UNSCHEDULED'
        try:
            opener = build_opener(HTTPHandler)
            request = Request(self.URL+"checkouts",
                              data=urlencode(data).encode('utf-8'))
            request.add_header(
                'Authorization', self.TOKEN)
            request.get_method = lambda: 'POST'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

    def delete_card(self, id):
        url = f"{self.URL}registrations/{id}"
        url += f'?entityId={self.ENTITY_ID}'
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=b'')
            request.add_header(
                'Authorization', self.TOKEN)
            request.get_method = lambda: 'DELETE'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason

    def get_payment_status(self, checkout_id):
        url = f"{self.URL}checkouts/{checkout_id}/payment"
        url += f'?entityId={self.ENTITY_ID}'
        try:
            opener = build_opener(HTTPHandler)
            request = Request(url, data=b'')
            request.add_header(
                'Authorization', self.TOKEN)
            request.get_method = lambda: 'GET'
            response = opener.open(request)
            return json.loads(response.read())
        except HTTPError as e:
            return json.loads(e.read())
        except URLError as e:
            return e.reason


# def order_checkout_id(user_request):

#     url = "https://eu-test.oppwa.com/v1/checkouts"
#     data = {
#         'entityId': user_request['entityId'],
#         'amount': user_request['amount'],
#         'currency': user_request['currency'],
#         'paymentType': user_request['paymentType']
#     }
#     if user_request['registrationId']:
#         data['registrations[0].id'] = user_request['registrationId']
#         data['standingInstruction.source'] = 'CIT'
#         data['standingInstruction.mode'] = 'REPEATED'
#         data['standingInstruction.type'] = 'UNSCHEDULED'
#     try:
#         opener = build_opener(HTTPHandler)
#         request = Request(url, data=urlencode(data).encode('utf-8'))
#         request.add_header(
#             'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
#         request.get_method = lambda: 'POST'
#         response = opener.open(request)
#         return json.loads(response.read())
#     except HTTPError as e:
#         return json.loads(e.read())
#     except URLError as e:
#         return e.reason


# def checkout_id(user_request):

#     url = "https://eu-test.oppwa.com/v1/checkouts"
#     data = {
#         'entityId': user_request.entityId,
#         'amount': user_request.amount,
#         'currency': user_request.currency,
#         'paymentType': user_request.paymentType
#     }
#     if user_request.registrationId:
#         data['registrations[0].id'] = user_request.registrationId
#         data['standingInstruction.source'] = 'CIT'
#         data['standingInstruction.mode'] = 'REPEATED'
#         data['standingInstruction.type'] = 'UNSCHEDULED'
#     try:
#         opener = build_opener(HTTPHandler)
#         request = Request(url, data=urlencode(data).encode('utf-8'))
#         request.add_header(
#             'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
#         request.get_method = lambda: 'POST'
#         response = opener.open(request)
#         return json.loads(response.read())
#     except HTTPError as e:
#         return json.loads(e.read())
#     except URLError as e:
#         return e.reason



# def get_payment_status(id, entityId=None):
#     url = f"https://eu-test.oppwa.com/v1/checkouts/{id}/payment"
#     url += f'?entityId={entityId}'
#     try:
#         opener = build_opener(HTTPHandler)
#         request = Request(url, data=b'')
#         request.add_header(
#             'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
#         request.get_method = lambda: 'GET'
#         response = opener.open(request)
#         return json.loads(response.read())
#     except HTTPError as e:
#         return json.loads(e.read())
#     except URLError as e:
#         return e.reason


# def delete_card(id, entityId):
#     url = f"https://eu-test.oppwa.com/v1/registrations/{id}"
#     url += f'?entityId={entityId}'
#     try:
#         opener = build_opener(HTTPHandler)
#         request = Request(url, data=b'')
#         request.add_header(
#             'Authorization', os.getenv('AUTHORIZATION_TOKEN'))
#         request.get_method = lambda: 'DELETE'
#         response = opener.open(request)
#         return json.loads(response.read())
#     except HTTPError as e:
#         return json.loads(e.read())
#     except URLError as e:
#         return e.reason


def get_payment_checkout_id(user_request, db: Session):
    
    customer_id = user_request.customer_id
    db_user_active = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()
    if db_user_active:
        if db_user_active.verification_status == "active":
            return HyperPayResponseView(user_request.entityId).generate_checkout_id(user_request)
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order")
            return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Customer does't exist!")
        return common_msg


def get_payment_status_api(entityId, checkout_id, db: Session):
    
    return HyperPayResponseView(entityId).get_payment_status(checkout_id)


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
    # hyperpay = delete_card(card_id, entityId)
    hyperpay = HyperPayResponseView(entityId).delete_card(card_id)

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
        