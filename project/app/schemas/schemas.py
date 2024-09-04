from typing import List, Optional

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginFrom(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class SupplierCreate(BaseModel):
    name: str
    contact_email: str
    phone_number: str


class SupplierResponse(BaseModel):
    name: str
    contact_email: str
    phone_number: str


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    supplier_id: int
    quantity: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    quantity: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    supplier_id: int
    quantity: int

    class Config:
        orm_mode = True


class OrderProductCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    products: List[OrderProductCreate]


class OrderProductResponse(BaseModel):
    product_id: int
    name: str
    quantity: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: str
    status: str
    products: List[OrderProductResponse]

    class Config:
        orm_mode = True
