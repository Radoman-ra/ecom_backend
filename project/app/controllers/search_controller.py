from typing import Any, Dict, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schemas import ProductResponse
from app.database.tables import Product, Category, Supplier
from datetime import datetime

async def search_for_products_controller(
    product_name: Optional[str],
    creation_date_from: Optional[str],
    creation_date_to: Optional[str],
    min_price: Optional[int],
    max_price: Optional[int],
    category_name: Optional[str],
    supplier_name: Optional[str],
    limit: int,
    offset: int,
    db: Session,
) -> Dict[str, Any]:
    query = db.query(Product)

    if product_name:
        query = query.filter(Product.name.ilike(f"%{product_name}%"))

    if creation_date_from:
        try:
            creation_date_from = datetime.strptime(
                creation_date_from, "%Y-%m-%d"
            )
            query = query.filter(Product.creation_date >= creation_date_from)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'creation_date_from' format, should be YYYY-MM-DD",
            )

    if creation_date_to:
        try:
            creation_date_to = datetime.strptime(creation_date_to, "%Y-%m-%d")
            query = query.filter(Product.creation_date <= creation_date_to)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid 'creation_date_to' format, should be YYYY-MM-DD",
            )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if category_name:
        query = query.join(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        )

    if supplier_name:
        query = query.join(Supplier).filter(
            Supplier.name.ilike(f"%{supplier_name}%")
        )

    total_products = query.count()

    products = query.offset(offset).limit(limit).all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found matching the criteria",
        )

    total_pages = (total_products + limit - 1) // limit

    return {
        "products": [ProductResponse.from_orm(product) for product in products],
        "total_products": total_products,
        "total_pages": total_pages,
        "current_page": (offset // limit) + 1,
        "limit": limit,
    }