from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from wayrem_admin.models import *
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
