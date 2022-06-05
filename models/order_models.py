from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from database import Base
import datetime as DT
from utility_services import common_services


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    ref_number = Column(String(255))
    customer_id = Column(ForeignKey('customers_master.id'))
    status = Column(Integer, nullable=True)
    sub_total = Column(Float())
    item_discount = Column(Float())
    item_margin = Column(Float())
    tax = Column(Float())
    tax_vat = Column(String(255), nullable=True)
    checkout_id = Column(String(255), nullable=True)
    shipping = Column(Float())
    total = Column(Float())
    promo = Column(String(255))
    discount = Column(Float())
    grand_total = Column(Float())
    order_ship_name = Column(String(255))
    order_ship_address = Column(String(255))
    order_billing_name = Column(String(255))
    order_billing_address = Column(String(255))
    order_city = Column(String(255))
    order_country = Column(String(255))
    order_ship_region = Column(String(255))
    order_ship_landmark = Column(String(255))
    order_ship_building_name = Column(String(255))
    order_ship_latitude = Column(String(255))
    order_ship_longitude = Column(String(255))
    order_phone = Column(String(255))
    order_email = Column(String(255))
    order_date = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    order_shipped = Column(Integer)
    order_tracking_number = Column(String(255))
    content = Column(String(255))
    delivery_status = Column(Integer(), default=1)
    order_type = Column(Integer(), default=24)
    delivery_charge = Column(String(255))


class OrderDetails(Base):
    __tablename__ = 'order_details'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    order_id = Column(ForeignKey('orders.id'))
    sku = Column(String(255))
    product_id = Column(Integer)
    product_name = Column(String(255))
    price = Column(Float())
    item_margin = Column(Float())
    discount = Column(Float())
    quantity = Column(Integer)


class OrderDeliveryLogs(Base):
    __tablename__ = 'order_delivery_logs'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    order_id = Column(ForeignKey('orders.id'))
    order_status_id = Column(Integer)
    user_id = Column(Integer)
    order_status_details = Column(String(255))
    log_date = Column(DateTime, nullable=False,
                      default=common_services.get_time())
    customer_view = Column(Integer)


class OrderTransactions(Base):
    __tablename__ = 'order_transactions'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer)
    order_id = Column(ForeignKey('orders.id'))
    code = Column(String(255), default='Test01')
    order_type = Column(Integer, nullable=True)
    payment_mode_id = Column(Integer, nullable=True)
    payment_status_id = Column(Integer, nullable=True)
    invoices_id = Column(Integer)
    created_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    updated_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    content = Column(String(255), nullable=True)
    bank_payment_image = Column(String(255), nullable=True)


class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    warehouse_id = Column(Integer)
    quantity = Column(Integer)
    inventory_type_id = Column(String(255))
    order_status = Column(String(255))
    created_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    updated_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())


class CustomerCart(Base):
    __tablename__ = 'customer_cart'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(Integer)
    product_id = Column(Integer)
    product_quantity = Column(Integer)
    created_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    updated_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())


class UserGrocery(Base):
    __tablename__ = 'grocery_master'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    grocery_name = Column(String(255))
    description = Column(String(1000))
    customer_id = Column(ForeignKey('customers_master.id'))
    address_id = Column(ForeignKey('customer_addresses.id'))
    created_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    updated_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())


class GroceryProducts(Base):
    __tablename__ = 'grocery_products'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    grocery_id = Column(ForeignKey('grocery_master.id'))
    product_id = Column(String(255))
    product_qty = Column(Integer)
    recurrence_nextdate = Column(String(255))


class RecurrentType(Base):
    __tablename__ = 'recurrent_type'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    name = Column(String(255))
    value = Column(String(255))
    status = Column(Boolean, default=True)


class RecurrenceGrocery(Base):
    __tablename__ = 'recurrence_grocery'
    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(Integer)
    grocery_id = Column(ForeignKey('grocery_master.id'))
    recurrenttype = Column(ForeignKey('recurrent_type.id'))
    recurrence_startdate = Column(
        String(255), nullable=False, default=DT.date.today())
    recurrence_nextdate = Column(String(255), nullable=False)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
    updated_at = Column(DateTime, nullable=False,
                        default=common_services.get_time())
