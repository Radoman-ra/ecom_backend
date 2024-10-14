from typing import List, Optional

from app.controllers.products_controller import (
    create_product,
    get_product_by_id,
    update_product,
    delete_product,
)
from app.schemas.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.database.database import get_db
from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
async def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return create_product(product_data, db, authorization)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return update_product(product_id, product_data, db, authorization)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return delete_product(product_id, db, authorization)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    return get_product_by_id(product_id, db)

