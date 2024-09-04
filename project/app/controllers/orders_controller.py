from schemas.schemas import OrderCreate, OrderResponse
from database.tables import Order
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_order(order_data: OrderCreate, db: Session) -> OrderResponse:
    order = Order(
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        status=order_data.status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderResponse.from_orm(order)


def get_all_orders(db: Session) -> list[OrderResponse]:
    orders = db.query(Order).all()
    return [OrderResponse.from_orm(order) for order in orders]


def update_order(
        order_id: int, order_data: OrderCreate, db: Session
) -> OrderResponse:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order.product_id = order_data.product_id
    order.quantity = order_data.quantity
    order.status = order_data.status
    db.commit()
    db.refresh(order)
    return OrderResponse.from_orm(order)


def delete_order(order_id: int, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    db.delete(order)
    db.commit()
