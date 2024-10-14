from typing import List, Optional

from fastapi import UploadFile
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
    contact_email: EmailStr
    phone_number: str


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class SupplierResponse(BaseModel):
    name: Optional[str]
    contact_email: Optional[EmailStr]
    phone_number: Optional[str]

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


    
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category_id: int
    supplier_id: int
    quantity: int
    photo: UploadFile = None


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
    photo_path: Optional[str]

    class Config:
        from_attributes = True
        
class PaginatedProductResponse(BaseModel):
    products: List[ProductResponse]
    total_products: int
    total_pages: int
    current_page: int


class OrderProductCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    products: List[OrderProductCreate]
    status: Optional[str] = None


class OrderProductResponse(BaseModel):
    product_id: int
    quantity: int
    status: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: str
    status: str
    products: List[OrderProductResponse]

    class Config:
        orm_mode = True
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[str] = None
