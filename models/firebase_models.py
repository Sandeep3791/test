from sqlalchemy import Column, Integer, String, Float, BigInteger, BLOB, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, date
import uuid
import datetime as DT
from sqlalchemy.sql import func


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


