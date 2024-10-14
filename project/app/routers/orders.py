from typing import Any, Dict, List, Optional

from app.controllers.orders_controller import (
    create_order,
    get_all_orders,
    get_orders_by_user,
    update_order,
    delete_order,
)
from app.schemas.schemas import OrderCreate, OrderResponse, OrderUpdate
from app.database.database import get_db
from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return create_order(order_data, db, authorization)

@router.get("/my-orders", response_model=Dict[str, Any])
async def fetch_my_orders(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
    limit: Optional[int] = Query(10, ge=1),
    offset: Optional[int] = Query(0, ge=0),
    status: Optional[str] = Query(None)
):
    return get_orders_by_user(db, authorization, limit, offset, status)




@router.get("/", response_model=List[OrderResponse])
async def fetch_all_orders(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
    limit: Optional[int] = Query(10, ge=1),
    offset: Optional[int] = Query(0, ge=0),
):
    return get_all_orders(db, authorization, limit, offset)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_existing_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return update_order(order_id, order_data, db, authorization)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_order(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    return delete_order(order_id, db, authorization)
