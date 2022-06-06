from fastapi_jwt_auth import AuthJWT
from schemas import user_schemas
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import user_address_services
import logging
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["USER ADDRESS"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.post('/add/customer/address')
def add_address_details(request: user_schemas.CustomerAddressSchema, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_addresses = user_address_services.add_address_details(request, db)
    return get_addresses


@router.get('/get/all/address')
def get_all_address(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_address_details = user_address_services.get_all_address(
        customer_id, db)
    return get_address_details


@router.put('/update/address')
def update_address(request: user_schemas.UpdateCustomerAddress, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    user = user_address_services.update_address(request, db)
    return user


@router.get('/get/billing/address')
def get_billing_address(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_address_details = user_address_services.get_billing_address(
        customer_id, db)
    return get_address_details


@router.put('/update/billing/address')
def update_billing_address(request: user_schemas.BillingAddressUpdate, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    user = user_address_services.update_billing_address(request, db)
    return user

@router.delete('/delete/customer/address')
def delete_customer_address(address_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    delete_address = user_address_services.delete_customer_address(
        address_id, db)
    return delete_address