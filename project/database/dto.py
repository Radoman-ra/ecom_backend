from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserDTO(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        orm_mode = True


class SupplierDTO(BaseModel):
    id: int
    name: str
    contact_email: EmailStr
    phone_number: Optional[str] = None

    class Config:
        orm_mode = True


class CategoryDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ProductDTO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    creation_date: datetime
    category_id: int
    supplier_id: int

    class Config:
        orm_mode = True


class OrderDTO(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    order_date: datetime
    status: str

    class Config:
        orm_mode = True
