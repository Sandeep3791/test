

import json

from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
    from urllib.request import HTTPHandler, Request, build_opener
except ImportError:
    from urllib import urlencode

    from urllib2 import HTTPError, HTTPHandler, Request, URLError, build_opener


def checkout_id(amount, currency, payment_type):
    url = "https://eu-test.oppwa.com/v1/checkouts"
    data = {
        'entityId': '8ac7a4c9767473e401767eff42341943',
        'amount': "{:.2f}".format(amount),
        'currency': currency,
        'paymentType': payment_type
    }
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=urlencode(data).encode('utf-8'))
        request.add_header(
            'Authorization', 'Bearer OGFjN2E0Yzk3Njc0NzNlNDAxNzY3ZWZkNzc1NjE5M2Z8azVKY1NtZlFYeQ==')
        request.get_method = lambda: 'POST'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason


def payment_status(id):
    url = f"https://eu-test.oppwa.com/v1/checkouts/{id}/payment"
    url += '?entityId=8ac7a4c9767473e401767eff42341943'
    try:
        opener = build_opener(HTTPHandler)
        request = Request(url, data=b'')
        request.add_header(
            'Authorization', 'Bearer OGFjN2E0Yzk3Njc0NzNlNDAxNzY3ZWZkNzc1NjE5M2Z8azVKY1NtZlFYeQ==')
        request.get_method = lambda: 'GET'
        response = opener.open(request)
        return json.loads(response.read())
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return e.reason


def get_payment_checkout_id(amount, currency, payment_type, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    return checkout_id(amount, currency, payment_type)


def get_payment_status(checkout_id, authorize: AuthJWT, db: Session):
    authorize.jwt_required()
    return payment_status(checkout_id)
