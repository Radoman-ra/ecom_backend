from schemas.schemas import CategoryCreate, CategoryResponse
from database.tables import Category
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_category(
    category_data: CategoryCreate, db: Session
) -> CategoryResponse:
    category = Category(
        name=category_data.name, description=category_data.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse.from_orm(category)


def get_all_categories(db: Session) -> list[CategoryResponse]:
    categories = db.query(Category).all()
    return [CategoryResponse.from_orm(category) for category in categories]


def update_category(
    category_id: int, category_data: CategoryCreate, db: Session
) -> CategoryResponse:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    category.name = category_data.name
    category.description = category_data.description
    db.commit()
    db.refresh(category)
    return CategoryResponse.from_orm(category)


def delete_category(category_id: int, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()
