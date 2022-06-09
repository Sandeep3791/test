
from pydantic import BaseModel
from typing import List

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
