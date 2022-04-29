from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.sqltypes import Boolean
from database import Base
from datetime import datetime
import uuid

class Business_type(Base):
    __tablename__ = 'business_type'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    business_type = Column(String(255))
    status = Column(Boolean, default=False)



class User(Base):
    __tablename__ = 'customers_master'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    business_type_id = Column(ForeignKey('business_type.id'))
    business_name = Column(String(255))
    email = Column(String(255))
    password = Column(String(255))
    contact = Column(BigInteger)
    profile_pic = Column(LONGTEXT, nullable=True)
    about = Column(String(1000), nullable=True)
    status = Column(Boolean, default=True)
    registration_number = Column(BigInteger)
    tax_number = Column(BigInteger)
    registration_docs_path = Column(String(255), nullable=True)
    tax_docs_path = Column(String(255), nullable=True)
    marrof_docs_path = Column(String(255), nullable=True)
    delivery_house_no_building_name = Column(String(255))
    delivery_road_name_Area = Column(String(255))
    delivery_landmark = Column(String(255))
    delivery_country = Column(String(255))
    delivery_region = Column(String(255))
    delivery_town_city = Column(String(255))
    billing_house_no_building_name = Column(String(255))
    billing_road_name_Area = Column(String(255))
    billing_landmark = Column(String(255))
    billing_country = Column(String(255))
    billing_region = Column(String(255))
    billing_town_city = Column(String(255))
    deliveryAddress_latitude = Column(String(255))
    deliveryAddress_longitude = Column(String(255))
    billlingAddress_Latitude = Column(String(255))
    billingAddress_longitude = Column(String(255))
    verification_status = Column(String(255), default="waiting for approval")
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())


class OtpVerification(Base):
    __tablename__ = 'customer_otp_verify'
    id = Column(String(255), primary_key=True, default=uuid.uuid4)
    email = Column(String(255))
    otp = Column(Integer)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class Customerotp(Base):
    __tablename__ = 'customer_otp'
    id = Column(String(255), primary_key=True, default=uuid.uuid4)
    otp = Column(Integer)
    email = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.now())


class CustomerAddresses(Base):
    __tablename__ = 'customer_addresses'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    customer_id = Column(ForeignKey('customers_master.id'))
    full_name = Column(String(255))
    contact = Column(BigInteger)
    house_no_building_name = Column(String(255))
    road_name_Area = Column(String(255))
    landmark = Column(String(255))
    country = Column(String(255))
    region = Column(String(255))
    town_city = Column(String(255))
    deliveryAddress_latitude = Column(String(255))
    deliveryAddress_longitude = Column(String(255))
    is_default = Column(Boolean, default=False)








# class StatusMaster(Base):
#     __tablename__= 'status_master'
#     id = Column(Integer(),autoincrement=True,primary_key=True,index=True)
#     name = Column(String(255))
#     status_color = Column(String(255))
#     status_type = Column(Integer)
#     sort_order = Column(Integer)
#     status = Column(Integer)




# notifications models

