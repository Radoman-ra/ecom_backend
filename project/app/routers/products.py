from typing import List, Optional

from controllers.products_controller import (
    create_product,
    get_all_products,
    update_product,
    delete_product,
)
from schemas.schemas import ProductCreate, ProductResponse, ProductUpdate
from dependencies.db_dependencies import get_db
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


@router.get("/", response_model=List[ProductResponse])
async def fetch_all_products(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
):
    return get_all_products(db, limit, offset)


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
