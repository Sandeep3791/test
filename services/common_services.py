from cgitb import html

from requests import session
import constants,jwt
from sqlalchemy.orm import Session
import logging
from schemas import common_schemas,user_schemas
from fastapi import FastAPI, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
import constants
from datetime import datetime
from pytz import timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI()

logger = logging.getLogger(__name__)



def get_time():
    now_utc = datetime.now(timezone('UTC'))
    time_now = now_utc.astimezone(timezone(constants.Default_time_zone))
    return time_now


def send_otp(to, subject, body,request , db:session):

    sender='support@wayrem.com'
    password='Wayrem@123'
    receiver = to
    smtpserver=smtplib.SMTP("smtp-mail.outlook.com",587)

    FROM = 'support@wayrem.com'
    TO = to
    REPLY_TO_ADDRESS = 'no-reply@wayrem.com'
    msg = MIMEMultipart('alternative')
    msg['To'] = TO
    msg['From'] = FROM
    msg['Subject'] = subject
    msg.add_header('reply-to', REPLY_TO_ADDRESS)
    mt_html = MIMEText(body, 'html')
    msg.attach(mt_html)
    mail = smtplib.SMTP('smtp-mail.outlook.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login('support@wayrem.com', 'Wayrem@123')
    mail.sendmail(FROM, TO, msg.as_string())
    print("Email Sent!")
    mail.quit()



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
    business_data = db.execute(f"SELECT * FROM {constants.Database_name}.business_type ;")
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

