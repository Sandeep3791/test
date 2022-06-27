from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from starlette import status


class CheckoutIdRequest(BaseModel):
    entityId: str
    amount: str
    currency: str
    paymentType: str
    registrationId: Optional[str]
    customer_id: int


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



