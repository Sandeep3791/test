from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from wayrem_supplier.models import *
import requests
import json


def send_email(to, subject, body):
    message = Mail(
        from_email='wayrem@hotmail.com',
        to_emails=to,
        subject=subject,
        html_content=body)
    try:
        sg = SendGridAPIClient(
            '[REDACTED].3HFHrgCCN81kEee5n_LCmeZbm8GrAVOXU1lClP5S_vI')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        print("Email Sent Successfully!!")
    except Exception as e:
        print("Email not sent!!")
        print(e)
        print(e.body)