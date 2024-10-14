from app.core.security import get_user_by_token
from app.utils.utils import check_admin_privileges
from app.schemas.schemas import SupplierCreate, SupplierResponse, SupplierUpdate
from app.database.tables import Supplier
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_supplier(
    supplier_data: SupplierCreate, db: Session, authorization: str
) -> SupplierResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    supplier = Supplier(
        name=supplier_data.name,
        contact_email=supplier_data.contact_email,
        phone_number=supplier_data.phone_number,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return SupplierResponse.from_orm(supplier)


def get_all_suppliers(
    db: Session, limit: int, offset: int
) -> list[SupplierResponse]:
    suppliers = db.query(Supplier).offset(offset).limit(limit).all()
    return [SupplierResponse.from_orm(supplier) for supplier in suppliers]


def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session,
    authorization: str,
) -> SupplierResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    if supplier_data.name:
        supplier.name = supplier_data.name

    if supplier_data.contact_email:
        supplier.contact_email = supplier_data.contact_email

    if supplier_data.phone_number:
        supplier.phone_number = supplier_data.phone_number

    db.commit()
    db.refresh(supplier)

    return SupplierResponse.from_orm(supplier)


def delete_supplier(
    supplier_id: int,
    db: Session,
    authorization: str,
):
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    db.delete(supplier)
    db.commit()

def get_supplier_by_id(
    supplier_id: int, db: Session
) -> SupplierResponse:
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    return SupplierResponse.from_orm(supplier)
