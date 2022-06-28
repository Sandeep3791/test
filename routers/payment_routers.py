
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends,UploadFile,File
import database
from schemas import payment_schemas
from sqlalchemy.orm import Session
from services import payment_services
import logging
from fastapi.security import HTTPBearer


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["PAYMENT"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.post('/get/payment/checkout/id')
def get_payment_checkout_id(user_request: payment_schemas.CheckoutIdRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_checkout_id(user_request, db)
    return response


@router.get('/get/payment/status')
def get_payment_checkout_id(entityId: str, checkout_id: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_status_api(entityId, checkout_id, db)
    return response



@router.get('/get/customer/cards')
def get_customer_cards(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_cards = payment_services.get_customer_cards(customer_id, db)
    return get_cards


@router.delete('/delete/customer/card')
def delete_customer_card(card_id: str, entityId: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    delete_card = payment_services.delete_customer_card(card_id, entityId, db)
    return delete_card


@router.get('/get/payment/types')
def get_payment_types(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_types(db)
    return response

@router.get('/get/payment/status/types')
def get_payment_status_types(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_status_types(db)
    return response

