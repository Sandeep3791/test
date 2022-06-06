
from fastapi_jwt_auth import AuthJWT
from schemas import cart_schemas, user_schemas
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import cart_services
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["CART"],
)
oauth2_scheme = HTTPBearer()


@router.post('/create/cart')
def create_cart(request: cart_schemas.AddToCart, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    products = cart_services.create_cart(request, db)
    return products


@router.get('/get/cart/products')
def get_cart_product(customer_id: int, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    get_product_details = cart_services.get_cart_product(
        customer_id, db)
    return get_product_details


@router.put('/update/cart/product')
def update_cart_product(request: cart_schemas.UpdateCartProducts, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    update_product = cart_services.update_cart_product(request, db)
    return update_product


@router.delete('/delete/cart/product')
def delete_cart(cart_id: int, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    delete_product = cart_services.delete_cart(cart_id, db)
    return delete_product

@router.delete('/clear/cart')
def clear_cart(customer_id: int, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    clear_cart_product = cart_services.clear_cart(customer_id, db)
    return clear_cart_product

@router.post('/add/multiple/cart/products')
def add_multiple_products(request: user_schemas.RequestAddMultiple, authorize: AuthJWT = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    products = cart_services.add_multiple_products(request, db)
    return products