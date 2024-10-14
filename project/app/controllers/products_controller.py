import os
import shutil
from app.core.security import get_user_by_token
from app.utils.utils import check_admin_privileges
from app.schemas.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.database.tables import Product
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
import hashlib

def hash_filename(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()

def create_product(
    product_data: ProductCreate,
    db: Session,
    authorization: str,
    photo: UploadFile = None,
) -> ProductResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    if photo:
        hashed_name = hash_filename(product_data.name)
        photo_path = f"static/images/{hashed_name}.png"
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
    else:
        photo_path = None

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        supplier_id=product_data.supplier_id,
        quantity=product_data.quantity,
        photo_path=photo_path,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse.from_orm(product)

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
        # Update the hashed filename if the name has changed
        hashed_name = hash_filename(product_data.name)
        product.photo_path = f"static/images/{hashed_name}.png"

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

def get_product_by_id(
    product_id: int,
    db: Session,
) -> ProductResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse.from_orm(product)
