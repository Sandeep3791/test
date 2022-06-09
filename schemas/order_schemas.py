
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from starlette import status

from services.payment_services import checkout_id


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


class OrderProducts(BaseModel):
    product_id: int
    product_quantity: int
    product_price: float

class OrderRequest(BaseModel):
    checkout_id: Optional[str]
    entityId: Optional[str]
    customer_id: int
    email: str
    contact: int
    country: str
    city: str
    shipping_region: str
    shipping_building_name: str
    shipping_landmark: str
    shipping_latitude: str
    shipping_longitude: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    delivery_fees: float
    products: List[OrderProducts]


class InitialOrderRequest(BaseModel):
    entityId: Optional[str]
    customer_id: int
    registrationId: Optional[str]
    email: str
    amount: str
    contact: int
    country: str
    city: str
    shipping_region: str
    shipping_building_name: str
    shipping_landmark: str
    shipping_latitude: str
    shipping_longitude: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    delivery_fees: float
    products: List[OrderProducts]

class CreateOrderRequest(BaseModel):
    ref_number: Optional[str]
    checkout_id: Optional[str]
    entityId: Optional[str]
    customer_id: int
    email: str
    contact: int
    country: str
    city: str
    shipping_region: str
    shipping_building_name: str
    shipping_landmark: str
    shipping_latitude: str
    shipping_longitude: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    delivery_fees: float
    products: List[OrderProducts]


class OrderedProducts(BaseModel):
    product_id: int
    latest_price: float


class OrderResponse1(BaseModel):
    status: str
    message: str
    data: OrderedProducts


class OrderResponse(BaseModel):
    status: str
    message: str


class RecurrenceRequest(BaseModel):
    customer_id: int
    grocery_id: int
    recurrenttype: Optional[str] = None
    recurrence_startdate: Optional[str] = None
    status: bool


class updateRecurrenceRequest(BaseModel):
    recurrent_order_id: int
    customer_id: int
    grocery_id: int
    recurrenttype: str
    recurrence_startdate: str
    status: bool


class OrdersProducts(BaseModel):
    product_id: int
    ordered_product_quantity: int
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
    review: Optional[str] = None


class OrderByIdDeliveryLogs(BaseModel):
    id: int
    status_name: str
    status_description: Optional[str] = None
    log_date: str


class OrderDetails(BaseModel):
    order_id: int
    order_ref_no: str
    sub_total: str
    item_discount: str
    tax_vat: str
    total: str
    grand_total: str
    email: str
    contact: int
    country: str
    city: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    order_date: str
    product_count: int
    order_status: int
    order_type: str
    invoice_id: Optional[str]
    delivery_logs: List[OrderByIdDeliveryLogs]
    products: List[OrdersProducts]


class ResponseMyOrders(BaseModel):
    customer_id: int
    orders: List[OrderDetails]


class FinalOrderResponse(BaseModel):
    status: str
    message: str
    data: ResponseMyOrders


class OrderDetailsbyid(BaseModel):
    order_id: int
    order_ref_no: str
    sub_total: str
    item_discount: str
    tax_vat: str
    total: str
    grand_total: str
    email: str
    contact: int
    country: str
    city: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    order_date: str
    product_count: int
    order_status: int
    order_type: str
    invoice_id: Optional[str]
    invoice_link: Optional[str]
    delivery_charges: float
    order_delivery_logs: List[OrderByIdDeliveryLogs]
    products: List[OrdersProducts]


class ResponseMyOrdersbyid(BaseModel):
    customer_id: int
    orders: List[OrderDetailsbyid]


class FinalOrderResponsebyid(BaseModel):
    status: str
    message: str
    data: ResponseMyOrdersbyid


class RecurrenceResponse(BaseModel):
    grocery_id: int
    recurrenttype: str
    recurrence_startdate: str
    status: bool


class RecurrenceFinalResponse(BaseModel):
    status: str
    message: str
    customer_id: int
    data: RecurrenceResponse


class RecurrenceOrderProducts(BaseModel):
    product_id: int
    product_quantity: int
    product_price: float


class PlaceRecurrenceOrder(BaseModel):
    customer_id: int
    email: str
    contact: int
    country: str
    city: str
    billing_name: str
    billing_address: str
    shipping_name: str
    shipping_address: str
    payment_type: str
    payment_status: str
    products: List[RecurrenceOrderProducts]


class Recurrentdata(BaseModel):
    recurrent_type_id: int
    recurrent_name: str


class RecurrentResponse(BaseModel):
    status: str
    message: str
    data: List[Recurrentdata]


class Deliveryfeedata(BaseModel):
    delivery_fees: Optional[float]
    free_delivery_after_amount: Optional[float]
    vat_value: str


class Getdeliveryfees(BaseModel):
    status: str
    message: str
    data: Deliveryfeedata

class ReferenceAndCheckoutIds(BaseModel):
    ref_number: str
    checkout_id: str

class InitialOrderResponse(BaseModel):
    status: str
    message: str
    data: ReferenceAndCheckoutIds
