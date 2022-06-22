from fastapi_jwt_auth import AuthJWT
from schemas import product_schemas
from fastapi import APIRouter, Depends
import database
from typing import Optional
from sqlalchemy.orm import Session
from services import product_services
import logging
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["PRODUCT"],
)

logger = logging.getLogger(__name__)
oauth2_schema = HTTPBearer()


@router.get('/get/product/details')
def get_product_details(customer_id: int, product_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_product_details(
        customer_id, product_id, db)
    return get_product_details


@router.get('/get/all/products')
def get_all_products(offset: str, customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_all_products(
        offset, customer_id, db)
    return get_product_details


@router.get('/get/category/products')
def get_category_products(customer_id: int, category_id: int, offset: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_category_products(
        customer_id, category_id, offset, db)
    return get_product_details

@router.get('/get/all/categories')
def get_all_categories(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_all_categories(db)
    return get_product_details

@router.get('/get/best/selling/products')
def get_best_selling_products(authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_best_selling_products(db)
    return get_product_details

@router.get('/get/featured/products')
def get_featured_products(customer_id: int, offset: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_featured_products(
        customer_id, offset, db)
    return get_product_details


@router.post('/add/favorite/Product')
def favorite_product(request: product_schemas.AddFavoriteProduct, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    products = product_services.favorite_Product(request, db)
    return products


@router.get('/get/favorite/products')
def get_favorite_product_details(customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_product_details = product_services.get_favorite_product_details(
        customer_id, db)
    return get_product_details


@router.put('/update/favorite/product')
def update_favorite_product(request: product_schemas.UpdateFavoriteProduct, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    update_product = product_services.update_favorite_product(
        request, db)
    return update_product


@router.delete('/delete/favorite/product')
def delete_product(id: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    delete_product = product_services.delete_favorite_product(id, db)
    return delete_product

@router.post('/create/product/rating')
def create_product_rating(request: product_schemas.CreateRating, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    create_rating = product_services.create_product_rating(request, db)
    return create_rating

@router.get('/product/search/filter')
def search_filter_products(offset:str,customer_id: int,authorize: AuthJWT = Depends(oauth2_schema), start_price: Optional[str] = None, end_price: Optional[str] = None, discount: Optional[bool] = None, featured: Optional[bool] = None, rating: Optional[bool] = None, newest: Optional[str] = None, category: Optional[str] = None,brand: Optional[str] = None, rating_value: Optional[int] = None, db: Session = Depends(database.get_db)):
    data = product_services.search_filter_products(offset,customer_id, start_price, end_price, discount, featured, rating, newest, category,brand,rating_value, db)
    return data

@router.get('/product/name/search')
def search_products_name(offset:str,customer_id: int,name: str, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    data = product_services.search_products_name(offset, customer_id,name, db)
    return data

@router.get('/get/discounted/products')
def get_discounted_products(offset: str, customer_id: int, authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_details = product_services.get_discounted_products(offset, customer_id, db)
    return get_details

@router.get('/get/all/subcategories')
def get_all_subcategories(category: str,authorize: AuthJWT = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    get_details = product_services.get_all_subcategories(category,db)
    return get_details

