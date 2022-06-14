from pydantic import BaseModel
from typing import List
from starlette import status


class StaticPages(BaseModel):
    id: int
    page_title: str
    page_slag: str
    page_url: str


class ResponseStaticPages(BaseModel):
    status: str
    message: str
    data: List[StaticPages]


class StateResponse(BaseModel):
    state: str
    loginext_code: str


class ListStateResponse(BaseModel):
    status: str
    message: str
    data: List[StateResponse]


class BusinessResponse(BaseModel):
    business_id: int
    business_name: str


class ListBusinessResponse(BaseModel):
    status: str
    message: str
    data: List[BusinessResponse]
