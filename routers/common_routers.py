from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
import database
from sqlalchemy.orm import Session
from utility_services import common_services

router = APIRouter(
    prefix="/v1",
    # dependencies=[Depends(get_bearer_header)],
    # responses={404: {"description": "Not found"},
    # 401:{"description":"Unauthorised"}},
    tags=["COMMON"],
)


@router.get('/get/static/pages')
def get_static_pages(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_static = common_services.get_static_pages(authorize, db)
    return get_static


@router.get('/get/state/code')
def get_state_code(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_state = common_services.get_state_code(authorize, db)
    return get_state


@router.get('/check/jwt')
def check_jwt_token(token: str, db: Session = Depends(database.get_db)):
    get_status = common_services.check_jwt_token(token, db)
    return get_status


@router.get('/business/type')
def get_business_type(authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    get_business = common_services.get_business_type(authorize, db)
    return get_business
