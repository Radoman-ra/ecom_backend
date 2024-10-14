from app.database.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

order_product_table = Table(
    "order_product",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(128))
    is_admin = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="user")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True, index=True)
    contact_email = Column(String(100), unique=True, index=True)
    phone_number = Column(String(20), unique=True, index=True)

    products = relationship("Product", back_populates="supplier")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(1000))

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String(100), index=True)
    description = Column(String(1000))
    price = Column(Integer, default=0, index=True)
    creation_date = Column(DateTime, default=func.now())
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id"), nullable=False, index=True
    )
    quantity = Column(Integer, default=0, index=True)
    photo_path = Column(String(200), nullable=True, unique=True)
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    orders = relationship(
        "Order", secondary=order_product_table, back_populates="products"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    order_date = Column(
        DateTime, default=func.now(), index=True, nullable=False
    )
    status = Column(String(50), default="Pending", index=True, nullable=False)

    user = relationship("User", back_populates="orders")
    products = relationship(
        "Product", secondary=order_product_table, back_populates="orders"
    )
