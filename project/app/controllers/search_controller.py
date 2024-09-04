from schemas.schemas import ProductResponse, SupplierResponse
from database.tables import Product, Supplier
from sqlalchemy.orm import Session


def search_products(query: str, db: Session) -> list[ProductResponse]:
    products = db.query(Product).filter(Product.name.ilike(f"%{query}%")).all()
    return [ProductResponse.from_orm(product) for product in products]


def search_suppliers(query: str, db: Session) -> list[SupplierResponse]:
    suppliers = (
        db.query(Supplier).filter(Supplier.name.ilike(f"%{query}%")).all()
    )
    return [SupplierResponse.from_orm(supplier) for supplier in suppliers]
