from typing import List

from controllers.orders_controller import (
    create_order,
    get_all_orders,
    update_order,
    delete_order,
)
from schemas.schemas import OrderCreate, OrderResponse
from dependencies.db_dependencies import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_new_order(
        order_data: OrderCreate, db: Session = Depends(get_db)
):
    return create_order(order_data, db)


@router.get("/", response_model=List[OrderResponse])
async def fetch_all_orders(db: Session = Depends(get_db)):
    return get_all_orders(db)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_existing_order(
        order_id: int, order_data: OrderCreate, db: Session = Depends(get_db)
):
    return update_order(order_id, order_data, db)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_order(order_id: int, db: Session = Depends(get_db)):
    return delete_order(order_id, db)
