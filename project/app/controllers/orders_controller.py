from core.security import get_user_by_token
from utils.utils import check_admin_privileges
from schemas.schemas import OrderCreate, OrderProductResponse, OrderResponse
from database.tables import Order, Product, order_product_table
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def create_order(
    order_data: OrderCreate,
    db: Session,
    authorization: str,
) -> OrderResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    order = Order(
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        status=order_data.status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderResponse.from_orm(order)


def get_all_orders(
    db: Session,
    authorization: str,
) -> list[OrderResponse]:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    # Fetch all orders
    orders = db.query(Order).all()

    # Prepare orders with products
    order_responses = []
    for order in orders:
        # Convert datetime to string
        order_date_str = order.order_date.isoformat()

        # Prepare products
        products = (
            db.query(Product)
            .join(
                order_product_table,
                Product.id == order_product_table.c.product_id,
            )
            .filter(order_product_table.c.order_id == order.id)
            .all()
        )
        product_responses = [
            OrderProductResponse(product_id=p.id, quantity=p.quantity)
            for p in products
        ]

        # Append to response list
        order_responses.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                order_date=order_date_str,
                status=order.status,
                products=product_responses,
            )
        )

    return order_responses


def update_order(
    order_id: int,
    order_data: OrderCreate,
    db: Session,
    authorization: str,
) -> OrderResponse:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
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


def delete_order(
    order_id: int,
    db: Session,
    authorization: str,
):
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    db.delete(order)
    db.commit()
