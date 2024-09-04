from typing import List

from controllers.categories_controller import (
    create_category,
    get_all_categories,
    update_category,
    delete_category,
)
from schemas.schemas import CategoryCreate, CategoryResponse
from dependencies.db_dependencies import get_db
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse)
async def create_new_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return create_category(category_data, db, authorization)


@router.get("/", response_model=List[CategoryResponse])
async def fetch_all_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_existing_category(
    category_id: int,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return update_category(category_id, category_data, db, authorization)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return delete_category(category_id, db, authorization)
