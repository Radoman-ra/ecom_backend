from schemas.schemas import SupplierCreate, SupplierResponse
from database.tables import Supplier
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_supplier(
    supplier_data: SupplierCreate, db: Session
) -> SupplierResponse:
    supplier = Supplier(
        name=supplier_data.name, contact_info=supplier_data.contact_info
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.from_orm(supplier)


def get_all_suppliers(db: Session) -> list[SupplierResponse]:
    suppliers = db.query(Supplier).all()
    return [SupplierResponse.from_orm(supplier) for supplier in suppliers]


def update_supplier(
    supplier_id: int, supplier_data: SupplierCreate, db: Session
) -> SupplierResponse:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    supplier.name = supplier_data.name
    supplier.contact_info = supplier_data.contact_info
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.from_orm(supplier)


def delete_supplier(supplier_id: int, db: Session):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    db.delete(supplier)
    db.commit()
