from sqlalchemy import Column, Integer, String, Float, BigInteger, BLOB, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, date
import uuid
import datetime as DT
from sqlalchemy.sql import func

class FavoriteProduct(Base):
    __tablename__ = 'Favorite_Product'
    id = Column(String(255), primary_key=True)
    customer_id = Column(String(255))
    product_id = Column(String(255))
    product_qty = Column(Integer)

class RatingReview(Base):
    __tablename__ = 'rating_review'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    customer_id = Column(Integer)
    product_id = Column(Integer)
    rating = Column(Integer)
    review = Column(String(200))
    date = Column(DateTime, nullable=False, default=datetime.now())


class ProductRating(Base):
    __tablename__ = 'product_rating'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    product_id = Column(Integer)
    rating = Column(Float)
    total_ratings = Column(Integer)
    total_reviews = Column(Integer)

