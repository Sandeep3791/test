from pydantic import BaseModel
from typing import List, Optional


class BankResponse(BaseModel):
    title: str
    bank_name: str
    account_name: str
    city: str
    branch: str
    iban: str
    account_no: Optional[str] = None
    swift_code: Optional[str] = None
    bank_key: Optional[str] = None


class ResponseBankData(BaseModel):
    status: str
    message: str
    data: List[BankResponse]
