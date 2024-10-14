from app.core.security import get_user_by_token
from app.utils.utils import check_admin_privileges
from app.schemas.schemas import CategoryCreate, CategoryResponse
from app.database.tables import Category
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_category(
    category_data: CategoryCreate,
    db: Session,
    authorization: str,
) -> CategoryResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    category = Category(
        name=category_data.name, description=category_data.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse.from_orm(category)


def get_all_categories(
    db: Session, limit: int, offset: int
) -> list[CategoryResponse]:
    categories = db.query(Category).offset(offset).limit(limit).all()
    return [CategoryResponse.from_orm(category) for category in categories]


def update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session,
    authorization: str,
) -> CategoryResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category_data.name:
        category.name = category_data.name

    if category_data.description:
        category.description = category_data.description

    db.commit()
    db.refresh(category)

    return CategoryResponse.from_orm(category)


def delete_category(
    category_id: int,
    db: Session,
    authorization: str,
):
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()
    
def get_category_by_id(
    category_id: int, db: Session
) -> CategoryResponse:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return CategoryResponse.from_orm(category)

