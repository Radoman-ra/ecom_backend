from typing import List

from controllers.search_controller import search_products, search_suppliers
from schemas.schemas import ProductResponse, SupplierResponse
from dependencies.db_dependencies import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/products", response_model=List[ProductResponse])
async def search_for_products(query: str, db: Session = Depends(get_db)):
    return search_products(query, db)


@router.get("/suppliers", response_model=List[SupplierResponse])
async def search_for_suppliers(query: str, db: Session = Depends(get_db)):
    return search_suppliers(query, db)
