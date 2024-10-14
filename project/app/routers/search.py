from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.schemas import ProductResponse
from app.controllers.search_controller import search_for_products_controller


router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/products", response_model=Dict[str, Any])
async def search_for_products(
    product_name: Optional[str] = Query(
        None, description="Search by product name"
    ),
    creation_date_from: Optional[str] = Query(
        None, description="Filter products created after this date", regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    creation_date_to: Optional[str] = Query(
        None, description="Filter products created before this date", regex=r"^\d{4}-\d{2}-\d{2}$"
    ),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    category_name: Optional[str] = Query(
        None, description="Search by category name"
    ),
    supplier_name: Optional[str] = Query(
        None, description="Search by supplier name"
    ),
    limit: int = Query(10, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    return await search_for_products_controller(
        product_name=product_name,
        creation_date_from=creation_date_from,
        creation_date_to=creation_date_to,
        min_price=min_price,
        max_price=max_price,
        category_name=category_name,
        supplier_name=supplier_name,
        limit=limit,
        offset=offset,
        db=db,
    )
