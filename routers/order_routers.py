
from fastapi_jwt_auth import AuthJWT
from schemas import order_schemas
from fastapi import APIRouter, Depends,BackgroundTasks
import database
from sqlalchemy.orm import Session
from services import order_services
import logging
from typing import Optional
from fastapi.security import HTTPBearer


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["ORDERS"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.post('/create/order')
def create_order(request: order_schemas.OrderRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db),background : BackgroundTasks = None):
    data = order_services.create_order(request, db,background)
    return data

@router.post('/initial/order')
def initialize_order(request: order_schemas.InitialOrderRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db),background : BackgroundTasks = None):
    data = order_services.initial_order(request, db,background)
    return data 

@router.post('/create/order/new')
def create_order_new(request: order_schemas.CreateOrderRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db),background : BackgroundTasks = None):
    data = order_services.create_order_new(request, db,background)
    return data


@router.get('/get/all/orders')
def get_all_orders(offset: str, customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_all_orders(
        offset, customer_id, db)
    return get_product_details


@router.get('/get/order/details')
def get_order_details(order_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_order_details(
        order_id, db)
    return get_product_details


@router.post('/create/recurrence/order')
def create_recurrence_order(request: order_schemas.RecurrenceRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    data = order_services.create_recurrence_order(request, db)
    return data


@router.put('/update/recurrence/order')
def update_recurrence_order(request: order_schemas.updateRecurrenceRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    data = order_services.update_recurrence_order(request, db)
    return data


@router.get('/get/all/recurrent/types')
def get_all_recurrent_type(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    grocery_details = order_services.get_all_recurrent_type(db)
    return grocery_details

@router.get('/get/delivery/fees')
def get_delivery_fees(address_id: Optional[int] = None ,authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_delivery = order_services.get_delivery_fees(address_id, db)
    return get_delivery

@router.get('/get/all/orders/filter')
def get_filters_orders(offset: str, customer_id: int, filter_id: int ,authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = order_services.get_filters_orders(
        offset, customer_id,filter_id, db)
    return get_product_details


@router.post('/get/pending/payment/checkout/id')
def get_pending_payment_checkout_id(user_request: order_schemas.PaymentCheckoutIdRequest, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = order_services.pending_payment_services(user_request, db)
    return response

@router.post('/clone/pending/payment')
def clone_order_payment(user_request: order_schemas.CloneOrderPayment, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    response = order_services.clone_order(user_request, db)
    return response

