import datetime as DT
import uuid
from datetime import date, datetime
from database import Base
from sqlalchemy import (BLOB, BigInteger, Column, DateTime, Float, ForeignKey,Integer, String)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Boolean


class CustomerDevice(Base):
    __tablename__ = 'customer_device'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    device_id = Column(String(255))
    device_type = Column(String(255))
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime(timezone=True),default=datetime.now() )

class CustomerNotification(Base):
    __tablename__ = 'customer_notification'

    id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    order_id = Column(BigInteger(),ForeignKey('orders.id'))
    title = Column(String(255))
    message = Column(String(255))
    created_at = Column(DateTime(timezone=True),default=datetime.now() )


