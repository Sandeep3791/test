
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Float
from database import Base
from pytz import timezone
from utility_services.common_services import get_time


class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    order_id = Column(Integer, nullable=True)
    transaction_id = Column(String(255), nullable=True)
    checkout_id = Column(String(255), nullable=True)
    response_body = Column(String(255), nullable=True)
    payment_type = Column(String(255), nullable=True)
    payment_brand = Column(String(255), nullable=True)
    amount = Column(String(255), nullable=True, default=0.00)
    status = Column(String(255), default="PAID", nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_time())
    updated_at = Column(DateTime(timezone=True), default=get_time())


class CustomerCard(Base):
    __tablename__ = "customer_cards"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    registration_id = Column(String(255))
    card_number = Column(String(50))
    expiry_month = Column(String(50))
    expiry_year = Column(String(50))
    card_holder = Column(String(255))
    card_type = Column(String(255))
    card_body = Column(String(255))
    card_brand = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=get_time())
    updated_at = Column(DateTime(timezone=True), default=get_time())


class CreditSettings(Base):
    __tablename__ = "credit_settings"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    credit_amount  = Column(Integer, nullable=True)
    time_period  = Column(Integer, nullable=True)
    
class CreditManagement(Base):
    __tablename__ = "credit_management"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    credit_rule_id = Column(ForeignKey('credit_settings.id'))
    used = Column(Float)
    available = Column(Float)
    updated_at = Column(DateTime(timezone=True), default=get_time())
    created_at = Column(DateTime(timezone=True), default=get_time())

