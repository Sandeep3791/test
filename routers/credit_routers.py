
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import credit_services
import logging
from fastapi.security import HTTPBearer


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["CREDITS"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.get('/get/credits')
def get_credits(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = credit_services.get_credits(customer_id, db)
    return response


@router.get('/get/credit/transactions')
def get_credits(customer_id: int, dues: bool = False, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = credit_services.get_credits_txn(customer_id, dues, db)
    return response


@router.get('/get/overdue/credits')
def get_overdue_credits(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = credit_services.get_overdue_credits(customer_id, db)
    return response
