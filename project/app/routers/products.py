from typing import List

from controllers.products_controller import (
    create_product,
    get_all_products,
    update_product,
    delete_product,
)
from schemas.schemas import ProductCreate, ProductResponse
from dependencies.db_dependencies import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
async def create_new_product(
    product_data: ProductCreate, db: Session = Depends(get_db)
):
    return create_product(product_data, db)


@router.get("/", response_model=List[ProductResponse])
async def fetch_all_products(db: Session = Depends(get_db)):
    return get_all_products(db)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)
):
    return update_product(product_id, product_data, db)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: int, db: Session = Depends(get_db)
):
    return delete_product(product_id, db)
