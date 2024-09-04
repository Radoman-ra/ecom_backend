from core.security import get_user_by_token
from utils.utils import check_admin_privileges
from schemas.schemas import ProductCreate, ProductResponse, ProductUpdate
from database.tables import Product
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_product(
    product_data: ProductCreate,
    db: Session,
    authorization: str,
) -> ProductResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        supplier_id=product_data.supplier_id,
        quantity=product_data.quantity,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse.from_orm(product)


def get_all_products(db: Session) -> list[ProductResponse]:
    products = db.query(Product).all()
    return [ProductResponse.from_orm(product) for product in products]


def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session,
    authorization: str,
) -> ProductResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.category_id is not None:
        product.category_id = product_data.category_id

    db.commit()
    db.refresh(product)

    return ProductResponse.from_orm(product)


def delete_product(
    product_id: int,
    db: Session,
    authorization: str,
):
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()
