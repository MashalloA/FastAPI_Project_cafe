from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    tastes = relationship("Taste", back_populates="product", cascade="all, delete-orphan")


class Taste(Base):
    __tablename__ = "tastes"

    id = Column(Integer, primary_key=True, index=True)
    taste = Column(String, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))  # ✅ СВЯЗЬ ПО ID

    product = relationship("Product", back_populates="tastes")
    info = relationship("Info", uselist=False, back_populates="taste", cascade="all, delete-orphan")


class Info(Base):
    __tablename__ = "info"

    id = Column(Integer, primary_key=True, index=True)
    in_stock = Column(Boolean)
    taste_id = Column(Integer, ForeignKey("tastes.id"))

    taste = relationship("Taste", back_populates="info")
    prices = relationship("Price", back_populates="info", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    volume = Column(Integer)
    price = Column(Integer)
    info_id = Column(Integer, ForeignKey("info.id"))

    info = relationship("Info", back_populates="prices")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    taste_id = Column(Integer, ForeignKey("tastes.id"))
    price_id = Column(Integer, ForeignKey("prices.id"))