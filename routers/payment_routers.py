
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends,UploadFile,File
import database
from schemas import payment_schemas
from sqlalchemy.orm import Session
from services import payment_services
import logging


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["PAYMENT"],
)

logger = logging.getLogger(__name__)



@router.post('/get/payment/checkout/id')
def get_payment_checkout_id(user_request: payment_schemas.CheoutIdRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_checkout_id(
        user_request, authorize, db)
    return response


@router.get('/get/payment/status')
def get_payment_checkout_id(entityId: str, checkout_id: str, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_status_api(
        entityId, checkout_id, authorize, db)
    return response


@router.get('/get/all/banks')
def get_all_banks(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_all_banks(authorize, db)
    return response


@router.post('/upload/bank/payment/image')
def upload_bank_payment_image(order_id: int, image: UploadFile = File(...), authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    user = payment_services.upload_bank_payment_image(
        order_id, image, authorize, db)
    return user


@router.get('/download/bank/payment/image')
def download_bank_payment_image(
        order_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = payment_services.download_bank_payment_image(
        order_id, authorize, db)
    return response


@router.get('/get/customer/cards')
def get_customer_cards(customer_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_cards = payment_services.get_customer_cards(customer_id, authorize, db)
    return get_cards


@router.delete('/delete/customer/card')
def delete_customer_card(card_id: str, entityId: str, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    delete_card = payment_services.delete_customer_card(
        card_id, entityId, authorize, db)
    return delete_card


@router.get('/get/payment/types')
def get_payment_types(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_types(authorize, db)
    return response
