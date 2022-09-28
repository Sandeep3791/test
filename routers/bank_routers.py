
from typing import Optional
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends,UploadFile,File
import database
from sqlalchemy.orm import Session
from services import bank_services
import logging
from fastapi.security import HTTPBearer


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["BANK"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.get('/get/all/banks')
def get_all_banks(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = bank_services.get_all_banks(db)
    return response


@router.post('/upload/bank/payment/image')
def upload_bank_payment_image(customer_id: str, order_id: int, pending_payment: Optional[bool] = False,image: UploadFile = File(...), authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    user = bank_services.upload_bank_payment_image(customer_id, order_id, pending_payment, image, db)
    return user


@router.get('/download/bank/payment/image')
def download_bank_payment_image(order_id: int, authorize: AuthJWT = Depends(oauth2_schema),db: Session = Depends(database.get_db)):
    response = bank_services.download_bank_payment_image(order_id, db)
    return response
