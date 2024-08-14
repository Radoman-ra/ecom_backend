import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="user")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, index=True)
    contact_email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)

    products = relationship("Product", back_populates="supplier")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer, default=0, index=True)
    creation_date = Column(DateTime, default=datetime.datetime.now)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id"), nullable=False, index=True
    )

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=0, index=True, nullable=False)
    order_date = Column(
        DateTime, default=datetime.datetime.now, index=True, nullable=False
    )
    status = Column(String, default="Pending", index=True, nullable=False)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
