from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from database import engine
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from models import user_models,firebase_models,order_models,product_models,payment_models,credit_models
from routers import cart_routers,common_routers,firebase_routers,grocery_routers,order_routers,product_routers,user_address_routers,user_routers,payment_routers,bank_routers,credit_routers
from schemas import user_schemas
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse


user_models.Base.metadata.create_all(bind=engine)
firebase_models.Base.metadata.create_all(bind=engine)
order_models.Base.metadata.create_all(bind=engine)
product_models.Base.metadata.create_all(bind=engine)
payment_models.Base.metadata.create_all(bind=engine)
credit_models.Base.metadata.create_all(bind=engine)


app = FastAPI()
middleware = [ Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])]
app = FastAPI(middleware=middleware)
app.include_router(user_routers.router)
app.include_router(user_address_routers.router)
app.include_router(cart_routers.router)
app.include_router(grocery_routers.router)
app.include_router(product_routers.router)
app.include_router(order_routers.router)
app.include_router(common_routers.router)
app.include_router(firebase_routers.router)
app.include_router(payment_routers.router)
app.include_router(bank_routers.router)
app.include_router(credit_routers.router)




@AuthJWT.load_config
def get_config():
    return user_schemas.Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
    
