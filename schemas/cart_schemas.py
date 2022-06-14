from pydantic import BaseModel
from typing import  List,Optional


class AddToCart(BaseModel):
    customer_id: int
    product_id: int
    product_quantity: int


class CartResponseNew(BaseModel):
    status: str
    message: str
    customer_id: int
    product_id: int
    product_quantity: int


class CartProducts(BaseModel):
    product_id: int
    product_quantity: int


class CartResponse(BaseModel):
    status: str
    message: str
    customer_id: int
    data: List[CartProducts]


class GetCartProducts(BaseModel):
    cart_id: int
    product_id: int
    product_quantity: int
    stock_quantity: int
    name: str
    SKU: str
    mfr_name: Optional[str] = None
    description: Optional[str] = None
    quantity_unit: str
    threshold: Optional[str] = None
    weight: Optional[str] = None
    weight_unit: str
    price: str
    discount: Optional[str] = None
    discount_unit: Optional[str] = None
    primary_image: str
    images: List[str]
    rating: float = None


class GetCartResponse(BaseModel):
    status: str
    message: str
    customer_id: int
    data: List[GetCartProducts]


class UpdateCartProducts(BaseModel):
    cart_id: int
    product_id: int
    product_quantity: int


class CartUpdateRes(BaseModel):
    status: str
    message: str
    data: UpdateCartProducts
