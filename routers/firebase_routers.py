from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import firebase_services
import logging
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["FIREBASE"],
)

logger = logging.getLogger(__name__)
oauth2_scheme = HTTPBearer()


@router.get('/get/device/id')
def get_device_id(customer_id:int, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    device_id = firebase_services.get_device_id(customer_id, db)
    return device_id

@router.get('/send/notification/list')
def send_notification_list(customer_id:int, authorize: AuthJWT = Depends(oauth2_scheme),db: Session = Depends(database.get_db)):
    send_notify = firebase_services.send_notification_list(customer_id, db)
    return send_notify


@router.delete('/delete/notification')
def delete_notification(customer_id:int, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    delete_noti = firebase_services.delete_notification(customer_id, db)
    return delete_noti

@router.post('/notification/status')
def notification_status(customer_id:int,device_id:str,is_active:bool, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    status_check = firebase_services.notification_status(customer_id,device_id,is_active, db)
    return status_check


@router.put('/deactivate/notification')
def notification_off(customer_id:int,device_id:str, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    stat_check = firebase_services.notification_off(customer_id,device_id, db)
    return stat_check
