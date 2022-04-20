import constants,jwt
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from mailersend import emails
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.responses import FileResponse
from sqlalchemy.sql.expression import null
from urllib3 import Retry
import constants
import random
import logging.config
import logging
from models import order_models
from schemas import common_schemas,user_schemas
from services import common_services
from fastapi import FastAPI, Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session, session
import random as r
from datetime import timedelta, datetime
import uuid
import os
import random
import datetime as DT


app = FastAPI()

logger = logging.getLogger(__name__)




# def send_otp(to, subject, body, request, db: Session):
#     message = Mail(
#         from_email=constants.MY_EMAIL,
#         to_emails=to,
#         subject=subject,
#         html_content=body)
#     try:
#         sg = SendGridAPIClient(
#             constants.SENDGRID_API_KEY)
#         response = sg.send(message)
#         print(response.status_code)
#         print(response.body)
#         print(response.headers)
#         print("Email Sent Successfully!!")
#     except Exception as e:
#         print("Email not sent!!")
#         print(e)
#         print(e.body)

def send_otp(to, subject, body, request, db: Session):
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNTIwY2IyZGRjMzI1ZDdjM2FjYjBlNjdlMDkxNDA2MjU1ZmQzNjAwNGNiZDIxZDdhZDE1YTc2MjkyZjhmNmZiZmY1MDNlOTg1NDllNjEyYWQiLCJpYXQiOjE2NDYzODg1MDcuNjU2MDM4LCJuYmYiOjE2NDYzODg1MDcuNjU2MDQxLCJleHAiOjQ4MDIwNjIxMDcuNjQ3Mzk1LCJzdWIiOiIyMjI3NyIsInNjb3BlcyI6WyJlbWFpbF9mdWxsIiwiZG9tYWluc19mdWxsIiwiYWN0aXZpdHlfZnVsbCIsImFuYWx5dGljc19mdWxsIiwidG9rZW5zX2Z1bGwiLCJ3ZWJob29rc19mdWxsIiwidGVtcGxhdGVzX2Z1bGwiLCJzdXBwcmVzc2lvbnNfZnVsbCJdfQ.n2M_k8A5451zVfTULF-xj_AQP6hE10rEG5NrBpk-iG_rySVTmQRYRtjPJUdkhrl1DzG3Ykt61y_BVTIoYVlUiza0F0HsBxrjzvYqHlBWV73lBUj1MyAeKf2jkhYpPgSHq7ZO6cLO0jVKw1oKy9Fr4Ijh72o15qJjjILIkcPF2yCfz_jnO7q21p9BokZfM_y1wAFHivXUKrjJt59TMt_I4A8zw3RiKbcd6gz8UItO1hRvaQ00zNTid-zL17stqPE63ieEOz14cLpN_IHCIQXZ_xrFOOp59xR7tHil1JQYlZ76__QJw4wj4MGhA7n0ap0GXQk98E4h14tiDZcf0PeNRD6nI_uC6nZK-S1ZziNaAWMF9fi-P1GwFMn-lXdf510RawzWsOI_F3SYVLRfN5B2iiID-QmEzXD-r7BuRNWAoGVCUP_h5ONLcP5qzpL8zQOH7nd6varQ3Luduphz8HdjaGoNRXJGoUjYJQ96X9ejlRcs8PJsiRx6O2Dtr6fiHozn5NSk_wM-f9DFFJxgzp51wBiL0fWaVJYFKa0c0dtY0087_RjRtjAzXrlE-uuUlEA0TzjCl12qZRAUOSZxABkKeBDRPDmFk44ElKGMgObD47HNwEq8RI2sKiubtUjP9RuVybaHvvfarqdSylqkvAjjVhgS6JK2YEbF3dM2Mrt-rcg"

    mailer = emails.NewEmail(api_key)
    # define an empty dict to populate with mail values
    mail_body = {}

    mail_from = {
        "name": "Wayrem",
        "email": "wayrem@admin-uat.wayrem.com",
    }

    recipients = [
        {
            "name": None,
            "email": to,
        }
    ]

    reply_to = [
        {
            "name": "Wayrem",
            "email": "wayrem@admin-uat.wayrem.com",
        }
    ]
    try:
        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(body, mail_body)
        # mailer.set_plaintext_content("This is the text content", mail_body)
        # mailer.set_reply_to(reply_to, mail_body)

        # using print() will also return status code and data
        print(mailer.send(mail_body))
        print("Email sent Successfully!!")
    except Exception as e:
        print("Email not sent!!")
        print(e)
        print(e.body)




def get_static_pages(authorize: AuthJWT, db: Session):
    # authorize.jwt_required()
    static_pages_data = db.execute(
        f"select * from {constants.Database_name}.static_pages")
    static_page_list = []
    for i in static_pages_data:
        page_url = i.slug
        page_link = "https://admin-stg.wayrem.com/home/pages/" + page_url
        data = common_schemas.StaticPages(
            id=i.id, page_title=i.page_title, page_slag=i.slug, page_url=page_link)
        static_page_list.append(data)
    response = common_schemas.ResponseStaticPages(
        status=status.HTTP_200_OK, message="All static pages data", data=static_page_list)
    return response


def get_state_code(authorize: AuthJWT, db: Session):
    # authorize.jwt_required()

    state_data = db.execute(
        f"SELECT * FROM {constants.Database_name}.state_code where status=1;")

    notf_data = []
    if state_data:
        for data in state_data:
            state = data.state
            loginext_code = data.loginext_code

            var = common_schemas.StateResponse(
                state=state, loginext_code=loginext_code)
            notf_data.append(var)

    if notf_data:
        response = common_schemas.ListStateResponse(
            status=status.HTTP_200_OK, message="State Details!", data=notf_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data for active status found!")
        return common_msg


def check_jwt_token(token, db: Session):
    try:
        jwt.decode(token, "secret", algorithms=["HS256"])
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Token is valid")
        return common_msg
    except jwt.ExpiredSignatureError:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Token is expired")
        return common_msg


def get_business_type(authorize: AuthJWT, db: Session):
    # authorize.jwt_required()
    business_data = db.execute(f"SELECT * FROM wayrem_stg_v1.business_type ;")
    business_list = []
    if business_data:
        for data in business_data:
            id = data.id
            name = data.business_type
            var = common_schemas.BusinessResponse(
                business_id=id, business_name=name)
            business_list.append(var)

    if business_list:
        response = common_schemas.ListBusinessResponse(
            status=status.HTTP_200_OK, message="Business type data!", data=business_list)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No data found!")
        return common_msg
