from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from starlette import status


class GetReview(BaseModel):
    customer_id: int
    customer_name: str
    customer_profile: str = None
    rating: int
    review: str
    date: str


class AllProductDetails(BaseModel):
    id: str
    name: str
    SKU: str
    mfr_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[str] = 0
    threshold: Optional[str] = None
    quantity_unit: Optional[str] = None
    weight: Optional[str] = None
    weight_unit: Optional[str] = None
    categories: List[str]
    price: Optional[str] = None
    discount: Optional[str] = None
    discount_unit: Optional[str] = None
    favorite: Optional[bool] = None
    favorite_product_uuid: Optional[str] = None
    primary_image: str
    images: List[str]
    rating: float = None
    review: List[GetReview] = None


class GetAllProducts(BaseModel):
    status: str
    message: str
    data: List[AllProductDetails]



class GetProductDetails(BaseModel):
    status: str
    message: str
    data: AllProductDetails


class GetAllProductsResponse(BaseModel):
    status: str
    message: str
    data: AllProductDetails


class Allcategories(BaseModel):
    category_id: int
    category_name: str
    category_tags: str
    category_image: str


class Getcategories(BaseModel):
    status: str
    message: str
    data: List[Allcategories]


class CreateRating(BaseModel):
    customer_id: int
    product_id: int
    rating: int
    review: Optional[str]


class CreateRatingResponse(BaseModel):
    status: str
    message: str
    data: CreateRating


class FavResponse(BaseModel):
    id: str
    customer_id: int
    product_id: str
    product_qty: int


class Addfavresponse(BaseModel):
    status: str
    message: str
    data: FavResponse



class AddFavoriteProduct(BaseModel):
    customer_id: int
    product_id: int
    product_qty: int




class UpdateFavoriteProduct(BaseModel):
    customer_id: int
    product_id: str
    product_qty: int


class FavoriteProduct(BaseModel):
    favorite_product_id: str
    product_id: str
    product_qty: int
    threshold: Optional[str] = None
    name: str
    SKU: str
    mfr_name: Optional[str] = None
    description: Optional[str] = None
    quantity_unit: str
    weight: Optional[str] = None
    weight_unit: str
    price: str
    discount: Optional[str] = None
    discount_unit: Optional[str] = None
    primary_image: str
    images: List[str]
    rating: float = None


class FavoriteProductResponse(BaseModel):
    status: str
    message: str
    customer_id: int
    data: List[FavoriteProduct]