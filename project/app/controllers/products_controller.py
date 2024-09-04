from schemas.schemas import ProductCreate, ProductResponse
from database.tables import Product
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_product(
    product_data: ProductCreate, db: Session
) -> ProductResponse:
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse.from_orm(product)


def get_all_products(db: Session) -> list[ProductResponse]:
    products = db.query(Product).all()
    return [ProductResponse.from_orm(product) for product in products]


def update_product(
    product_id: int, product_data: ProductCreate, db: Session
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.category_id = product_data.category_id
    db.commit()
    db.refresh(product)
    return ProductResponse.from_orm(product)


def delete_product(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()
