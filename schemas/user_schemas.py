from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from starlette import status
from services.user_services import refresh_token


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str
    device_id: str
    device_type: str


class OtpverifyResponse(BaseModel):
    status: str
    message: str
    data: Optional[str] = None
    otp: int


class ResponseCreateUser(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    password: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str
    profile_pic: str = None
    access_token: str
    refresh_token: str


class CreateUserResponse(BaseModel):
    status: str
    message: str
    data: ResponseCreateUser


class Login(BaseModel):
    email: str
    password: str
    device_id: str
    device_type: str


class LoginResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    profile_pic: Optional[str] = None
    about: Optional[str] = None
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str
    access_token: str
    refresh_token: str


class LoginResponseSchema(BaseModel):
    status: str
    message: str
    data: LoginResponse


class ProfileResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    profile_pic: Optional[str] = None
    registration_docs: Optional[str] = None
    tax_docs: Optional[str] = None
    marrof_docs: Optional[str] = None
    about: Optional[str] = None
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str
    reject_reason : Optional[str] = None


class ProfileResponseSchema(BaseModel):
    status: str
    message: str
    data: ProfileResponse


class OtpResponseCommonMessage(BaseModel):
    otp: int


class OtpVerificationrequest(BaseModel):
    email: str
    otp: int


class PwdResponseCommonMessage(BaseModel):
    status: str
    message: str
    data: OtpResponseCommonMessage


class ResponseCommonMessage(BaseModel):
    status: str
    message: str
    data: str = None


class ResetPassword(BaseModel):
    email: str
    old_password: str
    new_password: str
    confirm_password: str


class UserUpdate(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str


class ResponseUpdateUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    contact: int
    business_type: str
    business_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    registration_number: int
    tax_number: int
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    billlingAddress_Latitude: str
    billingAddress_longitude: str


class UpdateUserResponse(BaseModel):
    status: str
    message: str
    data: ResponseUpdateUser


class AuthEmail(BaseModel):
    email: str


class ForgotPassword(BaseModel):
    email: str
    otp: int
    new_password: str
    confirm_password: str



class FilterProductName(BaseModel):
    product_name: str


class CustomerAddressSchema(BaseModel):
    customer_id: int
    full_name: str
    contact: int
    house_no_building_name: str
    road_name_Area: str
    landmark: str
    country: str
    region: str
    town_city: str
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    default: bool


class CustomerAddressResponse2(BaseModel):
    customer_id: int
    full_name: str
    contact: int
    house_no_building_name: str
    road_name_Area: str
    landmark: str
    country: str
    region: str
    town_city: str
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str


class ResponseCommonMessageSchema(BaseModel):
    status: str
    message: str
    data: CustomerAddressResponse2


class CustomerAddressResponse(BaseModel):
    address_id: int
    full_name: str
    contact: int
    house_no_building_name: str
    road_name_Area: str
    landmark: str
    country: str
    region: str
    town_city: str
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    is_default: bool


class Responsedeliveryaddress(BaseModel):
    first_name: str
    last_name: str
    delivery_house_no_building_name: str
    delivery_road_name_Area: str
    delivery_landmark: str
    delivery_country: str
    delivery_region: str
    delivery_town_city:  str
    deliveryAddress_Latitude: str
    deliveryAddress_longitude: str


class ResponseAddressSchema(BaseModel):
    status: str
    message: str
    customer_id: int
    data: List[CustomerAddressResponse]


class UpdateCustomerAddress(BaseModel):
    customer_id: int
    address_id: int
    full_name: str
    contact: int
    house_no_building_name: str
    road_name_Area: str
    landmark: str
    country: str
    region: str
    town_city: str
    deliveryAddress_latitude: str
    deliveryAddress_longitude: str
    is_default: bool


class Updateaddressschema(BaseModel):
    status: str
    message: str
    data: UpdateCustomerAddress


# class UpdateDefaultAddress(BaseModel):
#         customer_id:int
#         delivery_house_no_building_name : str
#         delivery_road_name_Area :str
#         delivery_landmark :str
#         delivery_country :str
#         delivery_region :str
#         delivery_town_city :  str
#         deliveryAddress_latitude : str
#         deliveryAddress_longitude : str

# class ResponseDefaultaddress(BaseModel):
#         status: str
#         message: str
#         data: UpdateDefaultAddress


class ResponseBillingaddress(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    billlingAddress_Latitude: str
    billingAddress_longitude: str


class ResponseBillingaddressfinal(BaseModel):
    status: str
    message: str
    data: ResponseBillingaddress


class BillingAddressUpdate(BaseModel):
    customer_id: int
    billing_house_no_building_name: str
    billing_road_name_Area: str
    billing_landmark: str
    billing_country: str
    billing_region: str
    billing_town_city:  str
    billlingAddress_Latitude: str
    billingAddress_longitude: str


class ResponseBillingaddressupdate(BaseModel):
    status: str
    message: str
    data: BillingAddressUpdate



# -----------


class UploadProfiledata(BaseModel):
    path: str


class UploadProfile(BaseModel):
    status: str
    message: str
    data: UploadProfiledata


class Uploaddocsdata(BaseModel):
    registration_docs_path: str
    tax_docs_path: str
    marrof_docs_path: str


class Uploaddocs(BaseModel):
    status: str
    message: str
    data: Uploaddocsdata


class Responsedocs(BaseModel):
    file_path: str


class Responsedocspath(BaseModel):
    status: str
    message: str
    data: Responsedocs





class AddMultipleProducts(BaseModel):
    product_id: int
    product_quantity: int


class RequestAddMultiple(BaseModel):
    customer_id: int
    products: List[AddMultipleProducts]


class ResponseCartMultipleProducts(BaseModel):
    status: str
    message:  str
    customer_id: int
    products: List[AddMultipleProducts]


# Notification schemas


# class AllProductDetails2(BaseModel):
#         id: str
#         name: str
#         SKU: str
#         mfr_name: str
#         description: str
#         quantity: str
#         quantity_unit : str
#         weight: str
#         weight_unit: str
#         price: str
#         discount: str
#         primary_image: str
#         images : List[str]