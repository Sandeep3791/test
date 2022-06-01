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
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from datetime import datetime
from pytz import timezone
import email,requests,os,constants,calendar,smtplib
import email.mime.application

app = FastAPI()

logger = logging.getLogger(__name__)



def get_time():
    now_utc = datetime.now(timezone('UTC'))
    time_now = now_utc.astimezone(timezone(constants.Default_time_zone))
    return time_now


def send_otp(to, subject, body,request , db:Session, file_path = None,invoice_delete = None):

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

    # PDF attachment
    if file_path:
        attach_file_name = file_path
        filename=attach_file_name
        fp=open(filename,'rb')
        att = email.mime.application.MIMEApplication(fp.read(),_subtype="pdf")
        fp.close()
        att.add_header('Content-Disposition','attachment',filename="Invoice")
        msg.attach(att)
    else:
        pass

    mail = smtplib.SMTP('smtp-mail.outlook.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login('support@wayrem.com', 'Wayrem@123')
    mail.sendmail(FROM, TO, msg.as_string())
    print("Email Sent!")
    if invoice_delete:
        os.remove(invoice_delete)
    else:
        pass
    mail.quit()


def format_string(view_list,image_list,price_list,sup_name_list):
    x = f""
    y=0
    for i,j,k,m in zip(view_list,image_list,price_list,sup_name_list):
        pro_name = i.product_name
        pro_qty = i.quantity
        pro_price = k
        pro_image_path = j
        sup_name = m
        if sup_name==None:
            sup_name="Wayrem Supplier"
        y+=2
        x +=f"""<tr>
                                            <td width="20%">
                                                <img src="{pro_image_path}" alt="" style="width:100px;height:100px;object-fit:cover;border-radius:16px" class="CToWUd a6T" tabindex="0"><div class="a6S" dir="ltr" style="opacity: 0.01; left: 299px; top: 417.109px;"><div id=":pv" class="T-I J-J5-Ji aQv T-I-ax7 L3 a5q" title="Download" role="button" tabindex="0" aria-label="Download attachment " data-tooltip-class="a1V"><div class="akn"><div class="aSK J-J5-Ji aYr"></div></div></div></div>
                                            </td>
                                            <td width="60%" style="padding-left:0.5rem">
                                                <div>
                                                    <p style="margin:0;color:#152f50">{pro_name}</p>
                                                </div>
                                                <div><span style="color:#a8a8a8;font-size:.8rem">{sup_name}</span></div>
                                                <div><span style="font-weight:600;color:#152f50">{pro_price} SAR</span></div>
                                            </td>
                                            <td style="min-width:100px;text-align:end">x {pro_qty}
    
                                            </td>
                                    </tr>
                                """
    return x


def email_body(user_mail,order_id,order_view_list,image_list,order_type,ref_no,price_list,sup_name_list,db: Session):
    order_placed_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'order_placed_customer_notification' "
    if order_placed_query:
            order_template = db.execute(order_placed_query)
            subject = None
            body = None
            for template in order_template:
                subject = template.subject
                body = template.message_format
            to = user_mail

            pro_order_date = str(get_time())
            month = calendar.month_name[int(pro_order_date[5:7])]
            pro_order_date = month + \
                f" {str(pro_order_date[8:10])}, {str(pro_order_date[0:4])}{str(pro_order_date[10:16])}"
            pro_order_date = pro_order_date

            pro_status = db.execute(
                f"SELECT name from {constants.Database_name}.status_master where id=(SELECT payment_status_id from {constants.Database_name}.order_transactions where order_id={order_id}) ")
            for i in pro_status:
                pro1 = i[0]
            pro_order_status = pro1

            pro_pay_type = db.execute(
                f"SELECT name from {constants.Database_name}.status_master where id=(SELECT payment_mode_id from {constants.Database_name}.order_transactions where order_id={order_id}) ")
            for i in pro_pay_type:
                pro2 = i[0]
            pro_order_pay_type = pro2

            pro_type = db.execute(
                f"SELECT name from {constants.Database_name}.status_master where id={order_type}")
            for i in pro_type:
                pro3 = i[0]
            pro_order_type = pro3

            ret = format_string(order_view_list, image_list,price_list,sup_name_list)

            values = {
                'order_number': ref_no,
                'order_date_time': pro_order_date,
                'order_type': pro_order_type,
                'order_status': pro_order_status,
                'order_payment_type': pro_order_pay_type,
                'datas': ret
            }
            body = body.format(**values)
            val=[to, subject, body]
            
            return val



def invoice_saver(invoice_link_mail,ref_no):
    path = os.path.abspath('.')
    invoice_path = os.path.join(path,'invoice_folder')
    file_name = f"invoice_{ref_no}"
    completeName = os.path.join(invoice_path,file_name+".pdf")    
    url = invoice_link_mail
    file_content = requests.get(url, allow_redirects=True)
    open(completeName,'wb').write(file_content.content)
    


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

