from typing import Optional
from pydantic import BaseModel
from typing import Optional, List


class ResponseCustomerCredits(BaseModel):
    id: int
    customer_id: int
    used_credits: float
    available_credits: float
    total_credits : int

class ResponseCustomerCreditsFinal(BaseModel):
    status: str
    message: str
    data: ResponseCustomerCredits

class ResponseCustomerCreditsTxn(BaseModel):
    id: int
    credit_amount: float
    available : float
    credit_date: str
    due_date : str

class ResponseCustomerCreditsTxnFinal(BaseModel):
    status: str
    message: str
    data: List[ResponseCustomerCreditsTxn]