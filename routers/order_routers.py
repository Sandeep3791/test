
from fastapi_jwt_auth import AuthJWT
from schemas import order_schemas
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import order_services
import logging
from typing import Optional
router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["ORDERS"],
)

logger = logging.getLogger(__name__)


@router.post('/create/order')
def create_order(request: order_schemas.OrderRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    data = order_services.create_order(request, authorize, db)
    return data


@router.get('/get/all/orders')
def get_all_orders(offset: str, customer_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_all_orders(
        offset, customer_id, authorize, db)
    return get_product_details


@router.get('/get/order/details')
def get_order_details(order_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_order_details(
        order_id, authorize, db)
    return get_product_details


@router.post('/create/recurrence/order')
def create_recurrence_order(request: order_schemas.RecurrenceRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    data = order_services.create_recurrence_order(request, authorize, db)
    return data


@router.put('/update/recurrence/order')
def update_recurrence_order(request: order_schemas.updateRecurrenceRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    data = order_services.update_recurrence_order(request, authorize, db)
    return data


@router.get('/get/all/recurrent/types')
def get_all_recurrent_type(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    grocery_details = order_services.get_all_recurrent_type(authorize, db)
    return grocery_details

@router.get('/get/delivery/fees')
def get_delivery_fees(address_id: Optional[int] = None ,authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_delivery = order_services.get_delivery_fees(address_id, authorize, db)
    return get_delivery

@router.get('/get/all/orders/filter')
def get_filters_orders(offset: str, customer_id: int, filter_id: int ,authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_filters_orders(
        offset, customer_id,filter_id, authorize, db)
    return get_product_details