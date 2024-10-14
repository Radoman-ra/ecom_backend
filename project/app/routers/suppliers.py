from typing import List, Optional

from app.controllers.suppliers_controller import (
    create_supplier,
    get_all_suppliers,
    get_supplier_by_id,
    update_supplier,
    delete_supplier,
)
from app.schemas.schemas import SupplierCreate, SupplierResponse, SupplierUpdate
from app.database.database import get_db
from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponse)
async def create_new_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return create_supplier(supplier_data, db, authorization)


@router.get("/", response_model=List[SupplierResponse])
async def fetch_all_suppliers(
    limit: Optional[int] = Query(10, le=100),
    offset: Optional[int] = Query(0),
    db: Session = Depends(get_db),
):
    return get_all_suppliers(db, limit=limit, offset=offset)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_existing_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return update_supplier(supplier_id, supplier_data, db, authorization)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return delete_supplier(supplier_id, db, authorization)

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def fetch_supplier_by_id(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    return get_supplier_by_id(supplier_id, db)
