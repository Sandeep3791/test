from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from starlette import status


class CheoutIdRequest(BaseModel):
    entityId: str
    amount: str
    currency: str
    paymentType: str
    customer_id: int


class BankResponse(BaseModel):
    title: str
    bank_name: str
    account_name: str
    city: str
    branch: str
    iban: str


class ResponseBankData(BaseModel):
    status: str
    message: str
    data: List[BankResponse]


class ResponseCustomerCards(BaseModel):
    id: int
    card_number: str
    expiry_month: int
    expiry_year: int
    card_holder: str
    card_type: str
    card_brand: str
    card_id: str


class ResponseCustomerCardsFinal(BaseModel):
    status: str
    message: str
    data: List[ResponseCustomerCards]


class ResponsePaymentsType(BaseModel):
    id: int
    mode: str
    status: bool


class ResponsePaymentsTypeFinal(BaseModel):
    status: str
    message: str
    data: List[ResponsePaymentsType]

class ResponsePaymentstatus(BaseModel):
    id: int
    payment_status_name: str
    status: bool


class ResponsePaymentstatusFinal(BaseModel):
    status: str
    message: str
    data: List[ResponsePaymentstatus]
