from datetime import datetime
from typing import Optional
from fastapi.openapi.models import Contact
from matplotlib.pyplot import cla
from numpy import float64, product
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.dialects.mysql.types import LONGBLOB
from sqlalchemy.orm.sync import update
from sqlalchemy.sql.sqltypes import BLOB
from starlette import status



class Settings(BaseModel):
    authjwt_secret_key: str = "secret"




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
