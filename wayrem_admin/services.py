# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
from wayrem_admin.models import *
import requests
import json
from mailersend import emails
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to, subject, body):

    sender = 'support@wayrem.com'
    password = 'Wayrem@123'
    receiver = to
    smtpserver = smtplib.SMTP("smtp-mail.outlook.com", 587)
    try:
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
    except Exception as e:
        print(e)

# def send_email(to, subject, body):
#     message = Mail(
#         from_email='wayrem@hotmail.com',
#         to_emails=to,
#         subject=subject,
#         html_content=body)
#     try:
#         sg = SendGridAPIClient(
#             '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')
#         response = sg.send(message)
#         print(response.status_code)
#         print(response.body)
#         print(response.headers)
#         print("Email Sent Successfully!!")
#     except Exception as e:
#         print("Email not sent!!")
#         print(e)
#         print(e.body)


def delSession(request):
    try:
        for key in list(request.session.keys()):
            # skip keys set by the django system
            if not key.startswith("_") and not key.startswith("notification"):
                del request.session[key]
    except:
        pass
    return


def barcodeDetail(code):
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Accept': 'application/json',
    #     'Accept-Encoding': 'gzip,deflate',
    #     'user_key': 'only_for_dev_or_pro',
    #     'key_type': '3scale'
    # }
    try:
        headers = {
            'x-rapidapi-host': "barcode-lookup.p.rapidapi.com",
            # 'x-rapidapi-key': "2ppq23rl3qiilkkc0k315y1ft3ytxw"
        }
        # resp = requests.get(
        #     f'https://api.upcitemdb.com/prod/trial/lookup?upc={code}', headers=headers)
        resp = requests.get(
            f'https://api.barcodelookup.com/v3/products?barcode={code}&formatted=y&key=mnwhg43aos35mx2kusq6mtnrp4vbt0', headers=headers)
        data = json.loads(resp.text)
        return data
    except:
        pass


def inst_Supplier(value):
    return Supplier.objects.get(id=value)


def inst_Category(value):
    return Categories.objects.get(id=value)


def inst_Ingridient(value):
    return Ingredients.objects.filter(id=value).first()


def inst_Product(value):
    return Products.objects.filter(id=value).first()


def inst_Product_SKU(value):
    return Products.objects.filter(SKU=value).first()


def inst_SupplierProduct(value):
    return SupplierProducts.objects.filter(id=value).first()


def inst_Unit(value):
    return Unit.objects.get(id=value)


def inst_Warehouse(value):
    return Warehouse.objects.get(id=value)

# def send_email(to, subject, body):
#     api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNTIwY2IyZGRjMzI1ZDdjM2FjYjBlNjdlMDkxNDA2MjU1ZmQzNjAwNGNiZDIxZDdhZDE1YTc2MjkyZjhmNmZiZmY1MDNlOTg1NDllNjEyYWQiLCJpYXQiOjE2NDYzODg1MDcuNjU2MDM4LCJuYmYiOjE2NDYzODg1MDcuNjU2MDQxLCJleHAiOjQ4MDIwNjIxMDcuNjQ3Mzk1LCJzdWIiOiIyMjI3NyIsInNjb3BlcyI6WyJlbWFpbF9mdWxsIiwiZG9tYWluc19mdWxsIiwiYWN0aXZpdHlfZnVsbCIsImFuYWx5dGljc19mdWxsIiwidG9rZW5zX2Z1bGwiLCJ3ZWJob29rc19mdWxsIiwidGVtcGxhdGVzX2Z1bGwiLCJzdXBwcmVzc2lvbnNfZnVsbCJdfQ.n2M_k8A5451zVfTULF-xj_AQP6hE10rEG5NrBpk-iG_rySVTmQRYRtjPJUdkhrl1DzG3Ykt61y_BVTIoYVlUiza0F0HsBxrjzvYqHlBWV73lBUj1MyAeKf2jkhYpPgSHq7ZO6cLO0jVKw1oKy9Fr4Ijh72o15qJjjILIkcPF2yCfz_jnO7q21p9BokZfM_y1wAFHivXUKrjJt59TMt_I4A8zw3RiKbcd6gz8UItO1hRvaQ00zNTid-zL17stqPE63ieEOz14cLpN_IHCIQXZ_xrFOOp59xR7tHil1JQYlZ76__QJw4wj4MGhA7n0ap0GXQk98E4h14tiDZcf0PeNRD6nI_uC6nZK-S1ZziNaAWMF9fi-P1GwFMn-lXdf510RawzWsOI_F3SYVLRfN5B2iiID-QmEzXD-r7BuRNWAoGVCUP_h5ONLcP5qzpL8zQOH7nd6varQ3Luduphz8HdjaGoNRXJGoUjYJQ96X9ejlRcs8PJsiRx6O2Dtr6fiHozn5NSk_wM-f9DFFJxgzp51wBiL0fWaVJYFKa0c0dtY0087_RjRtjAzXrlE-uuUlEA0TzjCl12qZRAUOSZxABkKeBDRPDmFk44ElKGMgObD47HNwEq8RI2sKiubtUjP9RuVybaHvvfarqdSylqkvAjjVhgS6JK2YEbF3dM2Mrt-rcg"

#     mailer = emails.NewEmail(api_key)
#     # define an empty dict to populate with mail values
#     mail_body = {}

#     mail_from = {
#         "name": "Wayrem",
#         "email": "wayrem@admin-uat.wayrem.com",
#     }

#     recipients = [
#         {
#             "name": None,
#             "email": to,
#         }
#     ]

#     reply_to = [
#         {
#             "name": "Wayrem",
#             "email": "wayrem@admin-uat.wayrem.com",
#         }
#     ]
#     try:
#         mailer.set_mail_from(mail_from, mail_body)
#         mailer.set_mail_to(recipients, mail_body)
#         mailer.set_subject(subject, mail_body)
#         mailer.set_html_content(body, mail_body)
#         # mailer.set_plaintext_content("This is the text content", mail_body)
#         # mailer.set_reply_to(reply_to, mail_body)

#         # using print() will also return status code and data
#         print(mailer.send(mail_body))
#         print("Email sent Successfully!!")
#     except Exception as e:
#         print("Email not sent!!")
#         print(e)
#         print(e.body)
