
import json
import constants
import requests
from fastapi import Depends, FastAPI, status
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from httpx import delete
from matplotlib.pyplot import title
from models import firebase_models, order_models
from routers.product_routers import delete_product
from schemas import firebase_schemas, user_schemas
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import null


def push_notification_in_firebase(data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + constants.FIREBASE_TEST_SERVER_TOKEN,
    }
    body = {
        'notification': {'title': data.title,
                         'body': data.message
                         },
        'to': data.device_token,
        'priority': 'high',
        'data': {
            'order_id': data.order_id,
            'recurrent': None
        }

    }
    response = requests.post(
        constants.FIREBASE_URL, headers=headers, data=json.dumps(body))

    for i in response:
        print(i)
    return response


def get_device_id(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    customer_data = db.query(firebase_models.CustomerDevice).filter(
        firebase_models.CustomerDevice.customer_id == customer_id).all()

    tokens = []
    temp_list = []
    for customer in customer_data:
        temp = firebase_schemas.ListDeviceId(device_token=customer.device_id)
        tokens.append(temp)

    temp2 = firebase_schemas.DeviceId(customer_id=customer_id, data=tokens)
    temp_list.append(temp2)

    if customer_data:
        response = firebase_schemas.ResponseDeviceId(
            status=status.HTTP_200_OK, message="All Ids Fetched!", data=temp_list)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data for the customer found!")
        return common_msg


def send_notification_list(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    customer_data = db.execute(
        f"select * from {constants.Database_name}.customer_notification where customer_id = {customer_id} ORDER BY id DESC ; ")

    notf_data = []
    if customer_data:
        for customer in customer_data:
            t1 = customer.created_at.time()
            time = str(t1.replace(microsecond=0))
            date = str(customer.created_at.date())
            title = customer.title
            message = customer.message
            order_id = customer.order_id

            foreign_data = db.query(order_models.Orders).filter(
                order_models.Orders.id == order_id).first()
            order_ref = foreign_data.ref_number

            var = firebase_schemas.NotificationResponse(
                title=title, message=message, time=time, date=date, order_id=order_id, ref_no=order_ref)
            notf_data.append(var)

    if notf_data:
        response = firebase_schemas.Notify(
            status=status.HTTP_200_OK, message="All Notification!", data=notf_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data for the customer found!")
        return common_msg


def delete_notification(customer_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    data = db.query(firebase_models.CustomerNotification).filter(
        firebase_models.CustomerNotification.customer_id == customer_id).delete(synchronize_session=False)
    db.commit()
    if not data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data for the customer found!")
        return common_msg
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Notifications cleared Successfully!")
        return common_msg


def notification_status(customer_id, device_id, is_active: bool, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    customer_data = db.query(firebase_models.CustomerDevice).filter(
        firebase_models.CustomerDevice.customer_id == customer_id, firebase_models.CustomerDevice.device_id == device_id).first()

    if not customer_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data for the customer found!")
        return common_msg
    else:
        customer_data.is_active = is_active
        db.commit()

        common_msg = firebase_schemas.ResponseNotificationStatus(
            status=status.HTTP_200_OK, message=" status changed successfully", is_active=is_active)
        return common_msg


def notification_off(customer_id, device_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()

    customer_data = db.query(firebase_models.CustomerDevice).filter(
        firebase_models.CustomerDevice.customer_id == customer_id, firebase_models.CustomerDevice.device_id == device_id).all()

    if customer_data:
        for customer in customer_data:
            db.delete(customer)

        db.commit()
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message=" Device Records Deleted Successfully!")
        return common_msg
    else:

        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Data for Customer Found! ")
        return common_msg


