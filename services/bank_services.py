from services import firebase_services
from schemas import user_schemas, bank_schemas, firebase_schemas
from models import order_models, firebase_models
from sqlalchemy.orm import Session
from fastapi import status
import constants
import os
from utility_services import common_services


def get_all_banks(db: Session):

    bank_data = db.execute(
        f"select * from {constants.Database_name}.banks where status = True ; ")
    if bank_data.rowcount > 0:
        banks_list = []
        for data in bank_data:
            result = bank_schemas.BankResponse(title=data.title, bank_name=data.bank_name, account_name=data.account_name,
                                               city=data.city, branch=data.branch, iban=data.iban, account_no=data.account_no, swift_code=data.swift_code, bank_key=data.bank_key)
            banks_list.append(result)
        response = bank_schemas.ResponseBankData(
            status=status.HTTP_200_OK, message="All banks list", data=banks_list)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Banks found")
        return common_msg


def upload_bank_payment_image(customer_id, order_id, image, db: Session):

    order_data = db.query(order_models.OrderTransactions).filter(
        order_models.OrderTransactions.order_id == order_id).first()
    if not order_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Order id not found")
        return common_msg

    path = os.path.abspath('.')

    image_path = os.path.join(path, 'common_folder')
    inner_image_path = os.path.join(image_path, 'customer_banks')
    filepath = image.filename
    extension = filepath.split(".")[-1]
    db_path = f"bank_payment_orderId-{order_id}."+extension
    stored_path = os.path.join(
        inner_image_path, db_path)

    if os.path.exists(stored_path):
        os.remove(stored_path)

    with open(os.path.join(stored_path), "wb+") as file_object:
        file_object.write(image.file.read())
        file_object.close()

    order_data.bank_payment_image = db_path
    db.merge(order_data)
    db.commit()
    prfl_path = user_schemas.UploadProfiledata(path=db_path)
    common_msg = user_schemas.UploadProfile(
        status=status.HTTP_200_OK, message="success", data=prfl_path)

    try:
        customer_data = db.execute(
            f"select * from {constants.Database_name}.customer_device where customer_id = {customer_id} and is_active=True ;")

        setting_message = db.execute(
            f"select * from {constants.Database_name}.settings where settings.key = 'bank_receipt_upload_notification' ;")

        order_ref_no = db.execute(
            f"select ref_number from {constants.Database_name}.orders where orders.id = {order_id} ;")

        for msg in setting_message:
            message = msg.value
            title_message = msg.display_name

        for ref_no in order_ref_no:
            ref = ref_no[0]
        values = {
            "order_ref_no": ref
        }

        message = message.format(**values)

        if customer_data:
            for data in customer_data:
                notf = firebase_schemas.PushNotificationFirebase(
                    title=title_message, message=message, device_token=data.device_id, order_id=order_id)
                firebase_services.push_notification_in_firebase(notf)

            if notf:
                fire = firebase_models.CustomerNotification(
                    customer_id=customer_id, order_id=order_id, title=notf.title, message=notf.message, created_at=common_services.get_time())
                db.merge(fire)
                db.commit()
    except Exception as e:
        print(e)
    return common_msg


def download_bank_payment_image(order_id, db: Session):

    path = os.path.abspath('.')

    image_path = os.path.join(path, 'common_folder')
    common_dir_path = os.path.join(image_path, 'customer_banks')
    order_data = db.query(order_models.OrderTransactions).filter(
        order_models.OrderTransactions.order_id == order_id).first()
    if not order_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Order id not found")
    file_name = order_data.bank_payment_image
    if file_name in os.listdir(common_dir_path):
        file_path = constants.BANK_PAYMENT_IMAGES_PATH + file_name
        data2 = user_schemas.Responsedocs(file_path=file_path)
        response = user_schemas.Responsedocspath(
            status=status.HTTP_200_OK, message='success', data=data2)
        return response
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file_name}")
    return common_msg
