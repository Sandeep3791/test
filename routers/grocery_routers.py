
from fastapi_jwt_auth import AuthJWT
from schemas import grocery_schemas
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from services import grocery_services


router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["GROCERY"],
)


@router.post('/create/user/grocery')
def create_user_grocery(request: grocery_schemas.UserGrocerySchema, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    create_grocery = grocery_services.create_user_grocery(request, authorize, db)
    return create_grocery


@router.put('/update/user/grocery')
def update_user_grocery(request: grocery_schemas.UpdateGrocery, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    update_grocery = grocery_services.update_user_grocery(request, authorize, db)
    return update_grocery


@router.delete('/delete/user/grocery')
def delete_user_grocery(grocery_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    delete_grocery = grocery_services.delete_user_grocery(
        grocery_id, authorize, db)
    return delete_grocery


@router.get('/get/all/grocery')
def get_all_grocery(customer_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    grocery_details = grocery_services.get_all_grocery(customer_id, authorize, db)
    return grocery_details


@router.post('/create/grocery/products')
def create_grocery_products(request: grocery_schemas.CreateGroceryProducts,  authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    create_products = grocery_services.create_grocery_products(
        request, authorize, db)
    return create_products

@router.get('/get/all/grocery/products')
def get_grocery_products_details(grocery_id: int, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    grocery_details = grocery_services.get_grocery_products_details(
        grocery_id, authorize, db)
    return grocery_details


@router.put('/update/product/quantity')
def update_product_quantity(request: grocery_schemas.UpdateProductRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    product_qty = grocery_services.update_product_quantity(request, authorize, db)
    return product_qty


@router.delete('/delete/grocery/products')
def delete_grocery_products(request: grocery_schemas.DeleteProductsRequest, authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    delete_products = grocery_services.delete_grocery_products(
        request, authorize, db)
    return delete_products







