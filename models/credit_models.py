from enum import unique
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Float, true
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.sqltypes import Boolean
from database import Base
import uuid
from utility_services.common_services import get_time


class CreditSettings(Base):
    __tablename__ = "credit_settings"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    credit_amount = Column(Integer, nullable=True)
    time_period = Column(Integer, nullable=True)


class CreditManagement(Base):
    __tablename__ = "credit_management"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    credit_rule_id = Column(ForeignKey('credit_settings.id'))
    used = Column(Float)
    available = Column(Float)
    updated_at = Column(DateTime(timezone=True), default=get_time())
    created_at = Column(DateTime(timezone=True), default=get_time())


class CreditTransactionsLog(Base):
    __tablename__ = 'credit_transactions_logs'

    id = Column(Integer, primary_key=True)
    reference_id = Column(ForeignKey('credit_payment_reference.id'),nullable=True)
    credit_amount = Column(Float(asdecimal=True), nullable=False)
    available = Column(Float(asdecimal=True), nullable=False)
    credit_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    payment_status = Column(Boolean, default=False)
    is_refund = Column(Boolean, default=False)
    customer_id = Column(ForeignKey('customers_master.id'),
                         nullable=False, index=True)
    order_id = Column(BigInteger, ForeignKey(
        'orders.id'), nullable=False, index=True)
    credit_id = Column(Integer, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(Float, nullable=True)


class UserCreditRequest(Base):
    __tablename__ = 'customer_credit_request'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    requested_amount = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=get_time())
    created_at = Column(DateTime(timezone=True), default=get_time())



class CreditPaymentReference(Base):
    __tablename__ = "credit_payment_reference"

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    reference_no = Column(String(255),unique=True,nullable=True)
    bank_payment_file = Column(String(255), nullable=True)
    payment_type_id = Column(Integer)
    payment_status_id = Column(Integer)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=get_time())
    updated_at = Column(DateTime(timezone=True), default=get_time())


class CreditCycle(Base):
    __tablename__ = "credit_cycle"
    
    id = Column(Integer(), autoincrement=True,  primary_key=True, index=True)
    customer = Column(ForeignKey('customers_master.id'))
    credit_rule = Column(ForeignKey('CreditSettings.id'))
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_time())
    updated_at = Column(DateTime(timezone=True), default=get_time())