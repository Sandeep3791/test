from typing import Optional
from pydantic import BaseModel
from typing import Optional, List, Union


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
    credit_amount: Optional[float] = None
    available: Optional[float] = None
    credit_date: Optional[str] = None
    due_date: Optional[str] = None
    payment_status: bool
    is_refund : bool
    order_ref_no: Union[str, List[str]]
    valid_date: Optional[bool]
    paid_date: Optional[str] = None
    paid_amount: Optional[float] = None
    paid_credit_id: Optional[int] = None
    bank_pending:Optional[bool] = False
    bank_reject: Optional[bool] = False
    transaction_ref_id: Optional[int] = None
    bank_details: Optional[str] = None


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

class CreditDuesResponse(BaseModel):
    total_amount: float
    date: str
    customer_id: int
    reference_no:Optional[int]


class FinalDuesPayResponse(BaseModel):
    status: str
    message: str
    data: CreditDuesResponse


class UserCreditRequest(BaseModel):
    customer_id: int
    requested_amount: float


class UserCreditResponse(BaseModel):
    customer_id: int
    requested_amount: float
    


class FinalUserCreditResponse(BaseModel):
    status: str
    message: str
    data: UserCreditResponse


class CreditCheckNewUser(BaseModel):
    new_user: bool


class CheckUserCredit(BaseModel):
    status: str
    message: str
    data: CreditCheckNewUser

class CreditDuesbyBankRequest(BaseModel):
    credit_dues_ids: List[int]
    customer_id: int
    amount: float