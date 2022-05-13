
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
import database
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
def get_payment_checkout_id(amount: float, currency: str, payment_type: str, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_checkout_id(
        amount, currency, payment_type, authorize, db)
    return response


@router.get('/get/payment/status')
def get_payment_checkout_id(checkout_id: str, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    response = payment_services.get_payment_status(checkout_id, authorize, db)
    return response
