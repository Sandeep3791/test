from typing import Optional
from pydantic import BaseModel
from typing import Optional, List


class ResponseCustomerCredits(BaseModel):
    id: int
    customer_id: int
    used_credits: float
    available_credits: float
    total_credits: int


class ResponseCustomerCreditsFinal(BaseModel):
    status: str
    message: str
    data: ResponseCustomerCredits


class ResponseCustomerCreditsTxn(BaseModel):
    id: int
    credit_amount: float
    available: float
    credit_date: str
    due_date: str
    payment_status: bool
    order_ref_no: str
    valid_date: bool


class ResponseCustomerCreditsTxnFinal(BaseModel):
    status: str
    message: str
    data: List[ResponseCustomerCreditsTxn]


class ResponseCustomerCreditDue(BaseModel):
    status: str
    message: str
    data: Optional[ResponseCustomerCreditsTxn] = "No overdues"


class CreditDuesRequest(BaseModel):
    checkout_id: Optional[str]
    entityId: Optional[str]
    credit_dues_ids: List[int]
    customer_id: int
    amount: float
