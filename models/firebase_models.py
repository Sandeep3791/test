from datetime import datetime
from database import Base
from sqlalchemy import (BigInteger, Column, DateTime,
                        ForeignKey, Integer, String)
from sqlalchemy.sql.sqltypes import Boolean
from utility_services import common_services

import constants
from datetime import datetime
from pytz import timezone


def get_time():
    now_utc = datetime.now(timezone('UTC'))
    time_now = now_utc.astimezone(timezone(constants.Default_time_zone))
    return time_now


class CustomerDevice(Base):
    __tablename__ = 'customer_device'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    device_id = Column(String(255))
    device_type = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=get_time())


class CustomerNotification(Base):
    __tablename__ = 'customer_notification'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    order_id = Column(BigInteger(), ForeignKey('orders.id'))
    title = Column(String(255))
    message = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=get_time())
