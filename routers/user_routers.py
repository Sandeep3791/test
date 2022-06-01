from turtle import back
from fastapi_jwt_auth import AuthJWT
from starlette import status
from schemas import user_schemas
from fastapi import APIRouter, Depends, UploadFile, File,BackgroundTasks
import database
from sqlalchemy.orm import Session
from services import user_services
import logging
from typing import Optional
router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["CUSTOMER USERS"],
)

logger = logging.getLogger(__name__)


@router.post('/customer/registration')
def customer_user(request: user_schemas.User,authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db),background : BackgroundTasks = None):
    data = user_services.customer_user(request,authorize, db,background)
    return data


@router.post('/upload/profile/picture')
def upload_profile_picture(customer_id: int, profile_picture: UploadFile = File(...), authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    user = user_services.upload_profile_picture(
        customer_id, profile_picture, authorize, db)
    return user


@router.post('/upload/registration/docs')
def customer_registration_docs(customer_id: int, registration_docs: Optional[UploadFile] =File(None), tax_docs: Optional[UploadFile] =File(None),marrof_docs: Optional[UploadFile] =File(None), db: Session = Depends(database.get_db)):
    data = user_services.customer_registration_docs(
        customer_id, registration_docs, tax_docs,marrof_docs, db)
    return data


@router.post('/download/profile/picture')
def download_profile_picture(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_profile_picture(
        customer_id, authorize, db)
    return response


@router.post('/download/registration/docs')
def download_registration_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_registration_docs(
        customer_id, authorize, db)
    return response


@router.post('/download/tax/docs')
def download_tax_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_tax_docs(customer_id, authorize, db)
    return response

@router.post('/download/marrof/docs')
def download_marrof_docs(
        customer_id: int,
        authorize: AuthJWT = Depends(),
        db: Session = Depends(database.get_db)):
    response = user_services.download_marrof_docs(
        customer_id, authorize, db)
    return response

@router.post('/customer/login')
def customer_login(request: user_schemas.Login, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    data = user_services.customer_login(request, authorize, db)
    return data


@router.put('/update/profile')
def update_profile(request: user_schemas.UserUpdate, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    user = user_services.update_profile(request, authorize, db)
    return user


@router.get('/get/profile/details')
def get_profile_details(customer_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    authorize.jwt_required()
    get_address_details = user_services.get_profile_details(
        customer_id, authorize, db)
    return get_address_details


@router.post('/reset/password')
def reset_password(request: user_schemas.ResetPassword, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    reset_password = user_services.reset_password(request, authorize, db)
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

