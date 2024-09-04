from typing import List

from controllers.suppliers_controller import (
    create_supplier,
    get_all_suppliers,
    update_supplier,
    delete_supplier,
)
from schemas.schemas import SupplierCreate, SupplierResponse
from dependencies.db_dependencies import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponse)
async def create_new_supplier(
        supplier_data: SupplierCreate, db: Session = Depends(get_db)
):
    return create_supplier(supplier_data, db)


@router.get("/", response_model=List[SupplierResponse])
async def fetch_all_suppliers(db: Session = Depends(get_db)):
    return get_all_suppliers(db)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_existing_supplier(
        supplier_id: int,
        supplier_data: SupplierCreate,
        db: Session = Depends(get_db),
):
    return update_supplier(supplier_id, supplier_data, db)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_supplier(
        supplier_id: int, db: Session = Depends(get_db)
):
    return delete_supplier(supplier_id, db)
