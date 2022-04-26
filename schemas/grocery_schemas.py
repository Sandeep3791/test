
from datetime import datetime
from typing import Optional
from fastapi.openapi.models import Contact
from matplotlib.pyplot import cla
from numpy import product
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.dialects.mysql.types import LONGBLOB
from sqlalchemy.orm.sync import update
from sqlalchemy.sql.sqltypes import BLOB
from starlette import status
from services.user_services import refresh_token


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"




class GroceryProductsListResponse(BaseModel):
    product_id: int
    product_qty: int


class CreateGroceryProdResponse(BaseModel):
    status: str
    message: str
    grocery_id: int
    products: List[GroceryProductsListResponse]


class CreateGrocerySchema(BaseModel):
    id: int
    customer_id: int
    address_id: int
    grocery_name: str
    description: Optional[str] = None


class CreateGroceryResponse(BaseModel):
    status: str
    message: str
    data: CreateGrocerySchema


class UpdateGrocerySchemas(BaseModel):
    grocery_id: int
    grocery_name: str
    address_id: int
    description: Optional[str] = None


class UpdateGroceryResponse(BaseModel):
    status: str
    message: str
    data: UpdateGrocerySchemas


class ListGrocerDetailsResponse(BaseModel):
    grocery_id: int
    product_count: int
    customer_id: int
    address_id: int
    grocery_name: str
    description: Optional[str] = None
    recurrence_next_date: str = None


class ListGroceryDetails(BaseModel):
    status: str
    message: str
    data: List[ListGrocerDetailsResponse]


class UserGrocerySchema(BaseModel):
    customer_id: int
    grocery_name: str
    address_id: int
    description: Optional[str] = None


class UpdateGrocery(BaseModel):
    grocery_id: int
    grocery_name: str
    address_id: int
    description: Optional[str] = None


class GroceryProductsList(BaseModel):
    product_id: int
    product_qty: int


class CreateGroceryProducts(BaseModel):
    grocery_id: int
    products: List[GroceryProductsList]


class GroceryProdResp(BaseModel):
    product_id: int
    product_qty: int
    name: str
    SKU: str
    mfr_name: Optional[str] = None
    description: Optional[str] = None
    quantity: str
    quantity_unit: str
    threshold: Optional[str] = None
    weight: Optional[str]
    weight_unit: str
    categories: List[str]
    price: str
    discount: Optional[str]
    discount_unit: Optional[str] = None
    favorite: Optional[bool] = None
    favorite_product_uuid: Optional[str] = None
    primary_image: str
    images: List[str]


class GroceryRecurrenceprod(BaseModel):
    grocery_id: int
    grocery_name: str
    description: Optional[str] = None
    address_id: int
    recurrent_id: Optional[int] = None
    recurrenttype: Optional[str] = None
    recurrence_startdate: Optional[str] = None
    recurrence_status: Optional[int] = None
    products: List[GroceryProdResp]


class ResponseCommonMessageProducts(BaseModel):
    status: str
    message: str
    data:  GroceryRecurrenceprod


class DeleteProductsRequest(BaseModel):
    grocery_id: int
    product_id: int


class UpdateProductRequest(BaseModel):
    grocery_id: int
    product_id: int
    product_qty: int