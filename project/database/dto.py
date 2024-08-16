from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        orm_mode = True


class Supplier(BaseModel):
    id: int
    name: str
    contact_email: EmailStr
    phone_number: Optional[str] = None

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    creation_date: datetime
    category_id: int
    supplier_id: int

    class Config:
        orm_mode = True


class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    order_date: datetime
    status: str

    class Config:
        orm_mode = True
