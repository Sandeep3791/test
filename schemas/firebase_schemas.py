
from time import time
from typing import Optional,List
from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


class PushNotificationFirebase(BaseModel):
    title: Optional[str]
    message: Optional[str]
    device_token: Optional[str]
    order_id: Optional[str]
    recurrent: Optional[str] = None


class NotificationResponse(BaseModel):
    title: Optional[str]
    order_id: int
    ref_no: int
    message: Optional[str]
    time: Optional[str]
    date: str


class Notify(BaseModel):
    status: str
    message: str
    data: List[NotificationResponse]


class ListDeviceId(BaseModel):
    device_token: Optional[str]


class DeviceId(BaseModel):
    customer_id: int
    data: List[ListDeviceId]


class ResponseDeviceId(BaseModel):
    status: str
    message: str
    data: List[DeviceId]


class ResponseNotificationStatus(BaseModel):
    status: str
    message: str
    is_active: bool

    
    

