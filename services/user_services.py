
from fastapi.param_functions import Depends
import constants
import random
import logging
from models import user_models, firebase_models
from schemas import user_schemas
from utility_services import common_services
from fastapi import FastAPI, Depends, status,BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import random
from fastapi import Depends, FastAPI, status
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

app = FastAPI()

logger = logging.getLogger(__name__)


def customer_user(request, authorize: AuthJWT, db: Session,background_tasks: BackgroundTasks):
    user = db.query(user_models.User).filter(
        user_models.User.email == request.email).first()
    contact = db.query(user_models.User).filter(
        user_models.User.contact == request.contact).first()

    if user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message='User Already Exist')
        return common_msg
    if contact:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="This contact is already Exists!. Please use different contact")
        return common_msg
    if request.password != request.confirm_password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Your password and confirm password didn't match")
        return common_msg

    user_already_verified = db.query(user_models.OtpVerification).filter(
        user_models.OtpVerification.email == request.email, user_models.OtpVerification.verified == True).first()

    exist_user = db.query(user_models.OtpVerification).filter(
        user_models.OtpVerification.email == request.email).all()

    if not user_already_verified:
        random_no = random.randint(1000, 9999)
        to = request.email
        email_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'otp' "
        emails = db.execute(email_query)
        for email in emails:
            subject = email.subject
            body = email.message_format
        values = {
            'otp': random_no
        }
        body = body.format(**values)
        common_services.send_otp(to, subject, body, request, db)

        if exist_user:
            for user in exist_user:
                db.delete(user)
                db.commit()
        otp_data = user_models.OtpVerification(
            email=request.email, otp=random_no)
        db.merge(otp_data)
        db.commit()

    verified_user = db.query(user_models.OtpVerification).filter(
        user_models.OtpVerification.email == request.email).first()

    business_type_data = int(request.business_type)

    business_data = db.execute(
        f"SELECT * FROM {constants.Database_name}.business_type where id={business_type_data}")
    if business_data:
        for bu_data in business_data:
            bu_name = bu_data.business_type
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="buisness_type id not found")

    if verified_user.verified == True:
        data1 = user_models.User(first_name=request.first_name, last_name=request.last_name, business_type_id=business_type_data, business_name=request.business_name, email=request.email, password=request.password, contact=request.contact,
                                 registration_number=request.registration_number, tax_number=request.tax_number, delivery_house_no_building_name=request.delivery_house_no_building_name, delivery_road_name_Area=request.delivery_road_name_Area, delivery_landmark=request.delivery_landmark, delivery_country=request.delivery_country, delivery_region=request.delivery_region, delivery_town_city=request.delivery_town_city, billing_house_no_building_name=request.billing_house_no_building_name, billing_road_name_Area=request.billing_road_name_Area, billing_landmark=request.billing_landmark, billing_country=request.billing_country, billing_region=request.billing_region, billing_town_city=request.billing_town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude, billlingAddress_Latitude=request.billlingAddress_Latitude, billingAddress_longitude=request.billingAddress_longitude)
        db.merge(data1)
        db.commit()

        data = db.query(user_models.User).filter(
            user_models.User.email == request.email).first()
        f_name = data.first_name
        l_name = data.last_name
        full_name = f_name + l_name
        user_default_address = user_models.CustomerAddresses(customer_id=data.id, full_name=full_name, contact=request.contact, house_no_building_name=request.delivery_house_no_building_name, road_name_Area=request.delivery_road_name_Area, landmark=request.delivery_landmark,
                                                             country=request.delivery_country, region=request.delivery_region, town_city=request.delivery_town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude, is_default=True)
        db.merge(user_default_address)
        db.commit()

        email_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'customer_registration_notify'"
        emails = db.execute(email_query)
        subject = None
        email_ids = None
        body = None
        for email in emails:
            subject = email.subject
            email_ids = email.to_email
            body = email.message_format
        send_emails_to = email_ids.split(",")
        values = {
            'fullname': full_name,

            'link': f"{constants.global_link}/customer/customer-details/{data.id}/"
        }
        body = body.format(**values)
        for to in send_emails_to:
            background_tasks.add_task(common_services.send_otp, to, subject, body, request, db)
            
        sub = {"email": data.email, "id": data.id}
        access_token = authorize.create_access_token(
            subject=str(sub), expires_time=timedelta(days=10))
        file_path = None
        refresh_token = authorize.create_refresh_token(subject=str(sub))

        customer_id = data.id
        fire = db.query(firebase_models.CustomerDevice).filter(firebase_models.CustomerDevice.customer_id ==
                                                               customer_id, firebase_models.CustomerDevice.device_id == request.device_id).first()
        if not fire:
            fire = firebase_models.CustomerDevice(
                customer_id=customer_id, device_id=request.device_id, device_type=request.device_type)
            db.merge(fire)
            db.commit()
        else:
            pass

        res_data = user_schemas.ResponseCreateUser(customer_id=data.id, first_name=data.first_name, last_name=data.last_name, business_type=bu_name, business_name=data.business_name, email=data.email, password=data.password, contact=data.contact, registration_number=data.registration_number, tax_number=data.tax_number, delivery_house_no_building_name=data.delivery_house_no_building_name, delivery_road_name_Area=data.delivery_road_name_Area, delivery_landmark=data.delivery_landmark, delivery_country=data.delivery_country, delivery_region=data.delivery_region,
                                                   delivery_town_city=data.delivery_town_city, billing_house_no_building_name=data.billing_house_no_building_name, billing_road_name_Area=data.billing_road_name_Area, billing_landmark=data.billing_landmark, billing_country=data.billing_country, billing_region=data.billing_region, billing_town_city=data.billing_town_city, deliveryAddress_latitude=data.deliveryAddress_latitude, deliveryAddress_longitude=data.deliveryAddress_longitude, billlingAddress_Latitude=data.billlingAddress_Latitude, billingAddress_longitude=data.billingAddress_longitude, profile_pic=file_path, access_token=access_token, refresh_token=refresh_token
                                                   )
        response = user_schemas.CreateUserResponse(
            status=status.HTTP_200_OK, message="User Registered Successfully", data=res_data)
        verified_email_delete = db.query(user_models.OtpVerification).filter(
            user_models.OtpVerification.email == data.email).first()
        db.delete(verified_email_delete)
        db.commit()
        return response
    else:
        common_msg = user_schemas.OtpverifyResponse(
            status=status.HTTP_200_OK, message="You have to verify your email before registration",  otp=random_no)
        return common_msg


def upload_profile_picture(customer_id, profile_picture, db: Session):
    
    path = os.path.abspath('.')

    user_profile_path = os.path.join(path, 'common_folder')
    profile_path = os.path.join(
        user_profile_path, f"user_profile-{customer_id}.jpeg")

    if os.path.exists(profile_path):
        os.remove(profile_path)

    with open(os.path.join(profile_path), "wb+") as file_object:
        file_object.write(profile_picture.file.read())
        file_object.close()

    user_data = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()
    user_data.profile_pic = profile_path
    db.merge(user_data)
    db.commit()
    prfl_path = user_schemas.UploadProfiledata(path=profile_path)
    common_msg = user_schemas.UploadProfile(
        status=status.HTTP_200_OK, message="success", data=prfl_path)
    return common_msg


def customer_registration_docs(customer_id, registration_docs, tax_docs, marrof_docs, db):
    
    path = os.path.abspath('.')
    # print("-----------------------------------------------------------os path")
    # print(path)
    common_folder_path = os.path.join(path, 'common_folder')

    user_data = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()

    if user_data.verification_status == "active":
        resp = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message='User is already active!')
        return resp

    if not user_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message='Invalid Customer ID')
        return common_msg

    if registration_docs:
        a = registration_docs.filename
        s = a.split(".")[-1]
        reg_docs_path = os.path.join(
            common_folder_path, f"registration_docs-{customer_id}."+s)
        if os.path.exists(reg_docs_path):
            os.remove(reg_docs_path)
        if user_data:
            with open(reg_docs_path, "wb+") as file_object:
                file_object.write(registration_docs.file.read())
                file_object.close()
        user_data.registration_docs_path = reg_docs_path
        db.merge(user_data)
        db.commit()
    else:
        reg_docs_path = "null"

    if tax_docs:
        a = tax_docs.filename
        s = a.split(".")[-1]
        tax_docs_path = os.path.join(
            common_folder_path, f"tax_docs-{customer_id}."+s)
        if os.path.exists(tax_docs_path):
            os.remove(tax_docs_path)
        if user_data:
            with open(tax_docs_path, "wb+") as file_object:
                file_object.write(tax_docs.file.read())
                file_object.close()
        user_data.tax_docs_path = tax_docs_path
        db.merge(user_data)
        db.commit()
    else:
        tax_docs_path = "null"

    if marrof_docs:
        a = marrof_docs.filename
        s = a.split(".")[-1]
        marrof_docs_path = os.path.join(
            common_folder_path, f"marrof_docs-{customer_id}."+s)
        if os.path.exists(marrof_docs_path):
            os.remove(marrof_docs_path)
        if user_data:
            with open(marrof_docs_path, "wb+") as file_object:
                file_object.write(marrof_docs.file.read())
                file_object.close()
        user_data.marrof_docs_path = marrof_docs_path
        db.merge(user_data)
        db.commit()
    else:
        marrof_docs_path = "null"

    docs_data = user_schemas.Uploaddocsdata(
        registration_docs_path=reg_docs_path, tax_docs_path=tax_docs_path, marrof_docs_path=marrof_docs_path)

    resp = user_schemas.Uploaddocs(
        status=status.HTTP_200_OK, message='success', data=docs_data)
    if user_data.verification_status == "rejected":
        user_data.verification_status = "updated"
        db.merge(user_data)
        db.commit()
    return resp


def download_profile_picture(customer_id, db: Session):
    path = os.path.abspath('.')
    common_dir_path = os.path.join(path, 'common_folder')
    for file in os.listdir(common_dir_path):
        if file.split('-')[0] == "user_profile" and int(file.split('-')[1].split('.')[0]) == customer_id:
            file_path = constants.IMAGES_DIR_PATH + f'{file}'
            data2 = user_schemas.Responsedocs(file_path=file_path)
            response = user_schemas.Responsedocspath(
                status=status.HTTP_200_OK, message='success', data=data2)
            return response
            # return FileRes
            # return FileResponse(os.path.join(common_dir_path,f'{file}'), filename="profile_picture.jpeg",media_type="image")
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file}")
    return common_msg


def download_marrof_docs(customer_id, db: Session):
    path = os.path.abspath('.')
    common_dir_path = os.path.join(path, 'common_folder')
    for file in os.listdir(common_dir_path):
        if file.split('-')[0] == "marrof_docs" and int(file.split('-')[1].split('.')[0]) == customer_id:
            file_path = constants.IMAGES_DIR_PATH + f'{file}'
            data2 = user_schemas.Responsedocs(file_path=file_path)
            response = user_schemas.Responsedocspath(
                status=status.HTTP_200_OK, message='success', data=data2)
            return response
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file}")
    return common_msg


def download_registration_docs(customer_id, db: Session):
    path = os.path.abspath('.')
    common_dir_path = os.path.join(path, 'common_folder')
    for file in os.listdir(common_dir_path):
        if file.split('-')[0] == "registration_docs" and int(file.split('-')[1].split('.')[0]) == customer_id:
            file_path = constants.IMAGES_DIR_PATH + f'{file}'
            data2 = user_schemas.Responsedocs(file_path=file_path)
            response = user_schemas.Responsedocspath(
                status=status.HTTP_200_OK, message='success', data=data2)
            return response
            # return FileResponse(os.path.join(common_dir_path,f'{file}'), filename="registration_docs.pdf")

    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file}")
    return common_msg


def download_tax_docs(customer_id, db: Session):
    path = os.path.abspath('.')
    common_dir_path = os.path.join(path, 'common_folder')
    for file in os.listdir(common_dir_path):
        if file.split('-')[0] == "tax_docs" and int(file.split('-')[1].split('.')[0]) == customer_id:
            file_path = constants.IMAGES_DIR_PATH + f'{file}'
            data2 = user_schemas.Responsedocs(file_path=file_path)
            response = user_schemas.Responsedocspath(
                status=status.HTTP_200_OK, message='success', data=data2)
            return response
            # return FileResponse(os.path.join(common_dir_path,f'{file}'), filename="tax_docs.pdf")
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_404_NOT_FOUND, message=f"No file available for {file}")
    return common_msg


def customer_login(request, authorize: AuthJWT, db: Session):
    user = db.query(user_models.User).filter(
        user_models.User.email == request.email).first()
    if not user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message='Invalid Credentials')
        return common_msg
    customer_id = user.id
    fire = db.query(firebase_models.CustomerDevice).filter(firebase_models.CustomerDevice.customer_id ==
                                                           customer_id, firebase_models.CustomerDevice.device_id == request.device_id).first()
    if not fire:
        fire = firebase_models.CustomerDevice(
            customer_id=customer_id, device_id=request.device_id, device_type=request.device_type)
        db.merge(fire)
        db.commit()
    else:
        pass
    if fire.is_active == False:
        fire.is_active = True
        db.merge(fire)
        db.commit()

    if user.password != request.password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message='Invalid Credentials')
        return common_msg
    else:
        sub = {"email": user.email, "id": user.id}
        access_token = authorize.create_access_token(
            subject=str(sub), expires_time=timedelta(days=10)
        )
        try:
            if user.profile_pic:
                customer_id = user.id
                data = download_profile_picture(customer_id, db)
                x = dict(data.data)
                file_path = x.get("file_path")
            else:
                file_path = None
        except:
            file_path = None
        refresh_token = authorize.create_refresh_token(subject=str(sub))
        res_data = user_schemas.LoginResponse(customer_id=user.id, first_name=user.first_name, last_name=user.last_name, business_type=user.business_type_id, business_name=user.business_name, email=user.email, password=user.password, contact=user.contact, registration_number=user.registration_number, tax_number=user.tax_number, profile_pic=file_path, delivery_house_no_building_name=user.delivery_house_no_building_name, delivery_road_name_Area=user.delivery_road_name_Area, delivery_landmark=user.delivery_landmark, delivery_country=user.delivery_country, delivery_region=user.delivery_region,
                                              delivery_town_city=user.delivery_town_city, billing_house_no_building_name=user.billing_house_no_building_name, billing_road_name_Area=user.billing_road_name_Area, billing_landmark=user.billing_landmark, billing_country=user.billing_country, billing_region=user.billing_region, billing_town_city=user.billing_town_city, deliveryAddress_latitude=user.deliveryAddress_latitude, deliveryAddress_longitude=user.deliveryAddress_longitude, billlingAddress_Latitude=user.billlingAddress_Latitude, billingAddress_longitude=user.billingAddress_longitude, access_token=access_token, refresh_token=refresh_token)
        response = user_schemas.LoginResponseSchema(
            status=status.HTTP_200_OK, message='Login Successfully!', data=res_data)
        return response


def update_profile(request, db: Session):
    
    customer_add = db.query(user_models.CustomerAddresses).filter(
        user_models.CustomerAddresses.customer_id == request.id, user_models.CustomerAddresses.is_default == True).first()

    if not customer_add:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg

    customer_add.house_no_building_name = request.delivery_house_no_building_name
    customer_add.road_name_Area = request.delivery_road_name_Area
    customer_add.landmark = request.delivery_landmark
    customer_add.country = request.delivery_country
    customer_add.region = request.delivery_region
    customer_add.town_city = request.delivery_town_city
    customer_add.deliveryAddress_latitude = request.deliveryAddress_latitude
    customer_add.deliveryAddress_longitude = request.deliveryAddress_longitude
    db.merge(customer_add)
    db.commit()

    db_user_update = db.query(user_models.User).filter(
        user_models.User.id == request.id).first()

    if not db_user_update:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg

    db_user_update.first_name = request.first_name
    db_user_update.last_name = request.last_name
    db_user_update.email = request.email
    db_user_update.contact = request.contact
    db_user_update.business_type_id = request.business_type
    db_user_update.business_name = request.business_name
    db_user_update.delivery_house_no_building_name = request.delivery_house_no_building_name
    db_user_update.delivery_road_name_Area = request.delivery_road_name_Area
    db_user_update.delivery_landmark = request.delivery_landmark
    db_user_update.delivery_country = request.delivery_country
    db_user_update.delivery_region = request.delivery_region
    db_user_update.delivery_town_city = request.delivery_town_city
    db_user_update.billing_house_no_building_name = request.billing_house_no_building_name
    db_user_update.billing_road_name_Area = request.billing_road_name_Area
    db_user_update.billing_landmark = request.billing_landmark
    db_user_update.billing_country = request.billing_country
    db_user_update.billing_region = request.billing_region
    db_user_update.billing_town_city = request.billing_town_city
    db_user_update.registration_number = request.registration_number
    db_user_update.tax_number = request.tax_number
    db_user_update.deliveryAddress_latitude = request.deliveryAddress_latitude
    db_user_update.deliveryAddress_longitude = request.deliveryAddress_longitude
    db_user_update.billlingAddress_Latitude = request.billlingAddress_Latitude
    db_user_update.billingAddress_longitude = request.billingAddress_longitude
    db_user_update.updated_at = common_services.get_time()
    db.merge(db_user_update, db_user_update.updated_at)
    db.commit()

    business_data = db.execute(
        f"SELECT * FROM {constants.Database_name}.business_type where id={int(request.business_type)}")
    if not business_data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="buisness_type id not found")
    res_data = user_schemas.ResponseUpdateUser(first_name=request.first_name, last_name=request.last_name, business_type=request.business_type, business_name=request.business_name, email=request.email, contact=request.contact, registration_number=request.registration_number, tax_number=request.tax_number, delivery_house_no_building_name=request.delivery_house_no_building_name, delivery_road_name_Area=request.delivery_road_name_Area, delivery_landmark=request.delivery_landmark, delivery_country=request.delivery_country, delivery_region=request.delivery_region,
                                               delivery_town_city=request.delivery_town_city, billing_house_no_building_name=request.billing_house_no_building_name, billing_road_name_Area=request.billing_road_name_Area, billing_landmark=request.billing_landmark, billing_country=request.billing_country, billing_region=request.billing_region, billing_town_city=request.billing_town_city, deliveryAddress_latitude=request.deliveryAddress_latitude, deliveryAddress_longitude=request.deliveryAddress_longitude, billlingAddress_Latitude=request.billlingAddress_Latitude, billingAddress_longitude=request.billingAddress_longitude)
    common_msg = user_schemas.UpdateUserResponse(
        status=status.HTTP_200_OK, message="User Updated Successfully !", data=res_data)
    return common_msg


def get_profile_details(customer_id, db: Session):
    user = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()
    if not user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg
    try:
        if user.profile_pic:
            customer_id = user.id
            data = download_profile_picture(customer_id, db)
            x = dict(data.data)
            file_path = x.get("file_path")
        else:
            file_path = None
    except:
        file_path = None
    try:
        if user.registration_docs_path:
            data1 = download_registration_docs(customer_id, db)
            x = dict(data1.data)
            register_docs_path = x.get("file_path")
        else:
            register_docs_path = None
    except:
        register_docs_path = None
    try:
        if user.tax_docs_path:
            data1 = download_tax_docs(customer_id, db)
            x = dict(data1.data)
            tax_docs_path = x.get("file_path")
        else:
            tax_docs_path = None
    except:
        tax_docs_path = None

    try:
        if user.marrof_docs_path:
            data1 = download_marrof_docs(customer_id, db)
            x = dict(data1.data)
            marrof_docs_path = x.get("file_path")
        else:
            marrof_docs_path = None
    except:
        marrof_docs_path = None


    if  user.reject_reason :
        reason = user.reject_reason
    else:
        reason = None


    res_data = user_schemas.ProfileResponse(customer_id=user.id, first_name=user.first_name, last_name=user.last_name, business_type=user.business_type_id, business_name=user.business_name, email=user.email, password=user.password, contact=user.contact, registration_number=user.registration_number, tax_number=user.tax_number, profile_pic=file_path, registration_docs=register_docs_path, tax_docs=tax_docs_path, marrof_docs=marrof_docs_path, delivery_house_no_building_name=user.delivery_house_no_building_name, delivery_road_name_Area=user.delivery_road_name_Area, delivery_landmark=user.delivery_landmark, delivery_country=user.delivery_country,delivery_region=user.delivery_region, delivery_town_city=user.delivery_town_city, billing_house_no_building_name=user.billing_house_no_building_name, billing_road_name_Area=user.billing_road_name_Area, billing_landmark=user.billing_landmark, billing_country=user.billing_country, billing_region=user.billing_region, billing_town_city=user.billing_town_city, deliveryAddress_latitude=user.deliveryAddress_latitude, deliveryAddress_longitude=user.deliveryAddress_longitude, billlingAddress_Latitude=user.billlingAddress_Latitude, billingAddress_longitude=user.billingAddress_longitude,reject_reason = reason)
    response = user_schemas.ProfileResponseSchema(
        status=status.HTTP_200_OK, message='Profile data', data=res_data)
    return response


def reset_password(request, db: Session):
    
    user = db.query(user_models.User).filter(
        user_models.User.email == request.email).first()

    if not user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User Doesn't Exist!")
        return common_msg
    if user.password != request.old_password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Your Old Password Is Incorrect")
        return common_msg
    if request.new_password != request.confirm_password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Password Doesn't Match")
        return common_msg
    if request.old_password == request.new_password or request.old_password == request.confirm_password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="please enter new password")
        return common_msg

    if request.new_password == request.confirm_password:
        user.password = request.new_password
        user.updated_at = common_services.get_time()
        db.merge(user, user.updated_at)
        db.commit()
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Password Reset Successfully!")
        return common_msg


def generate_passcode(request, db: Session):
    email_user = db.query(user_models.User).filter(
        user_models.User.email == request.email).first()
    if not email_user:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Please Enter Correct Email")
        return common_msg
    random_no = random.randint(1000, 9999)
    to = request.email
    subject = constants.SUBJECT
    body = f'your otp is {random_no}'
    common_services.send_otp(to, subject, body, request, db)
    exit_user = db.query(user_models.Customerotp).filter(
        user_models.User.email == request.email).all()
    if exit_user:
        for user in exit_user:
            db.delete(user)
            db.commit()
    db_otp = user_models.Customerotp(otp=random_no, email=to)
    db.merge(db_otp)
    db.commit()
    data = user_schemas.OtpResponseCommonMessage(otp=random_no)
    common_msg = user_schemas.PwdResponseCommonMessage(
        status=status.HTTP_200_OK, message="OTP Sent Successfully !", data=data)
    return common_msg


def verify_otp(request, db):
    data = db.query(user_models.Customerotp).filter(user_models.Customerotp.email ==
                                                    request.email, user_models.Customerotp.otp == request.otp).first()
    email_verified = db.query(user_models.OtpVerification).filter(
        user_models.OtpVerification.email == request.email, user_models.OtpVerification.otp == request.otp).first()

    if email_verified:
        if email_verified.otp == request.otp:
            email_verified.verified = True
            db.merge(email_verified)
            db.commit()
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_200_OK, message="Your Email verified successfully")
            return common_msg
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message="The OTP You Entered Is Wrong")
            return common_msg
    if not data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="The Email or OTP You Entered is Wrong")
        return common_msg

    if data:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Your OTP verified successfully")
        db.delete(data)
        db.commit()
        return common_msg


def forgot_password(request, db: Session):
    # data = db.query(user_models.Customerotp).filter(user_models.Customerotp.email==request.email).first()
    data2 = db.query(user_models.User).filter(
        user_models.User.email == request.email).first()

    # if not data:
    #     common_msg = user_schemas.ResponseCommonMessage(status = status.HTTP_404_NOT_FOUND, message="The Email You Entered is Wrong")
    #     return common_msg
    # if data.otp != request.otp:
    #     common_msg = user_schemas.ResponseCommonMessage(status = status.HTTP_404_NOT_FOUND, message="The OTP You Entered Is Wrong")
    #     return common_msg
    if request.new_password != request.confirm_password:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="The New Password and Confirm Password Doesn't Match")

        return common_msg
    data2.password = request.new_password
    db.merge(data2)
    db.commit()
    # db.delete(data)
    # db.commit()
    common_msg = user_schemas.ResponseCommonMessage(
        status=status.HTTP_200_OK, message="Password Updated Successfully !")
    return common_msg


def refresh_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()
    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
