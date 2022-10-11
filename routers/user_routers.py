from fastapi_jwt_auth import AuthJWT
from starlette import status
from schemas import user_schemas
from fastapi import APIRouter, Depends, UploadFile, File,BackgroundTasks, Form
import database
from sqlalchemy.orm import Session
from services import user_services
import logging
from typing import Optional
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["CUSTOMER USERS"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.post('/customer/registration')
def customer_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    contact: int = Form(...),
    business_type: str = Form(...),
    business_name: str = Form(...),
    delivery_house_no_building_name: str = Form(...),
    delivery_road_name_Area: str = Form(...),
    delivery_landmark: Optional[str] = Form(None),
    delivery_country: str = Form(...),
    delivery_region: str = Form(...),
    delivery_town_city:  str = Form(...),
    billing_house_no_building_name: str = Form(...),
    billing_road_name_Area: str = Form(...),
    billing_landmark: Optional[str]  = Form(None),
    billing_country: str = Form(...),
    billing_region: str = Form(...),
    billing_town_city:  str = Form(...),
    registration_number: int = Form(...),
    tax_number: int = Form(...),
    deliveryAddress_latitude: str = Form(...),
    deliveryAddress_longitude: str = Form(...),
    billlingAddress_Latitude: str = Form(...),
    billingAddress_longitude: str = Form(...),
    device_id: str = Form(...),
    device_type: str = Form(...) ,
    registration_docs :UploadFile =File(None), tax_docs : UploadFile =File(None), marrof_docs : UploadFile =File(None), authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db), background : BackgroundTasks = None):
    request = user_schemas.User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
            confirm_password = confirm_password,
            contact= contact,
            business_type = business_type,
            business_name = business_name,
            delivery_house_no_building_name = delivery_house_no_building_name,
            delivery_road_name_Area = delivery_road_name_Area,
            delivery_landmark = delivery_landmark,
            delivery_country = delivery_country,
            delivery_region = delivery_region,
            delivery_town_city = delivery_town_city,
            billing_house_no_building_name = billing_house_no_building_name,
            billing_road_name_Area = billing_road_name_Area,
            billing_landmark =  billing_landmark,
            billing_country = billing_country,
            billing_region = billing_region,
            billing_town_city = billing_town_city,
            registration_number = registration_number,
            tax_number = tax_number,
            deliveryAddress_latitude = deliveryAddress_latitude,
            deliveryAddress_longitude = deliveryAddress_longitude,
            billlingAddress_Latitude = billlingAddress_Latitude,
            billingAddress_longitude = billingAddress_longitude,
            device_id = device_id,
            device_type = device_type
        )
    data = user_services.customer_user(request, registration_docs, tax_docs, marrof_docs, authorize, db, background)
    return data


@router.post('/upload/profile/picture')
def upload_profile_picture(customer_id: int, profile_picture: UploadFile = File(...), authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    user = user_services.upload_profile_picture(
        customer_id, profile_picture, db)
    return user


@router.post('/upload/registration/docs')
def customer_registration_docs(customer_id: int, registration_docs: Optional[UploadFile] =File(None), tax_docs: Optional[UploadFile] =File(None),marrof_docs: Optional[UploadFile] =File(None), db: Session = Depends(database.get_db),background : BackgroundTasks = None):
    data = user_services.customer_registration_docs(
        customer_id, registration_docs, tax_docs,marrof_docs, db,background)
    return data


@router.post('/download/profile/picture')
def download_profile_picture(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_profile_picture(
        customer_id, db)
    return response


@router.post('/download/registration/docs')
def download_registration_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_registration_docs(
        customer_id, db)
    return response


@router.post('/download/tax/docs')
def download_tax_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_tax_docs(customer_id, db)
    return response

@router.post('/download/marrof/docs')
def download_marrof_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_marrof_docs(
        customer_id, db)
    return response

@router.post('/customer/login')
def customer_login(request: user_schemas.Login, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    data = user_services.customer_login(request, authorize, db)
    return data


@router.put('/update/profile')
def update_profile(request: user_schemas.UserUpdate, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    user = user_services.update_profile(request, db)
    return user


@router.get('/get/profile/details')
def get_profile_details(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_address_details = user_services.get_profile_details(customer_id, db)
    return get_address_details


@router.post('/reset/password')
def reset_password(request: user_schemas.ResetPassword, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    reset_password = user_services.reset_password(request, db)
    return reset_password


@router.post('/generate/otp', status_code=status.HTTP_202_ACCEPTED)
def generate_passcode(request: user_schemas.AuthEmail, db: Session = Depends(database.get_db)):
    fpass = user_services.generate_passcode(request, db)
    return fpass


@router.post('/verify/otp')
def verify_passcode(request: user_schemas.OtpVerificationrequest, db: Session = Depends(database.get_db)):
    res = user_services.verify_otp(request, db)
    return res


@router.post('/forgot/password', status_code=status.HTTP_202_ACCEPTED)
def forgot_password(request: user_schemas.ForgotPassword, db: Session = Depends(database.get_db)):
    fpass = user_services.forgot_password(request, db)
    return fpass

# @router.put('/update/default/address')
# def update_default_address(request: user_schemas.UpdateDefaultAddress,authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
#     user= user_services.update_default_address(request,authorize, db)
#     return user

# @router.post('/processing/recurrence/order')
# def processing_recurrence_order(db: Session = Depends(database.get_db)):
#     data = user_services.processing_recurrence_order(db)
#     return data

@router.put('/account/deactivate')
def account_deactivate(customer_id: int,authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    data = user_services.account_deactivate(customer_id, db)
    return data


