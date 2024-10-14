from typing import List, Optional
from app.core.security import get_user_by_token
from app.utils.utils import check_admin_privileges
from app.schemas.schemas import (
    OrderCreate,
    OrderProductResponse,
    OrderResponse,
    OrderUpdate,
)
from app.database.tables import Order, Product, order_product_table
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import math
from typing import Dict, Any


def create_order(
    order_data: OrderCreate,
    db: Session,
    authorization: str,
) -> OrderResponse:
    user = get_user_by_token(authorization, db)

    order = Order(
        user_id=user.id,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for product_data in order_data.products:

        product = (
            db.query(Product)
            .filter(Product.id == product_data.product_id)
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        if product.quantity < product_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough quantity for product {product.name}. Available: {product.quantity}, requested: {product_data.quantity}",
            )

        product.quantity -= product_data.quantity
        db.commit()

        db.execute(
            order_product_table.insert().values(
                order_id=order.id,
                product_id=product.id,
                quantity=product_data.quantity,
            )
        )

    db.commit()

    products_in_order = (
        db.query(Product)
        .join(
            order_product_table, Product.id == order_product_table.c.product_id
        )
        .filter(order_product_table.c.order_id == order.id)
        .all()
    )

    product_responses = [
        OrderProductResponse(product_id=p.id, quantity=p.quantity)
        for p in products_in_order
    ]

    return OrderResponse(
        id=order.id,
        user_id=user.id,
        order_date=order.order_date.isoformat(),
        status=order.status,
        products=product_responses,
    )

def get_orders_by_user(
    db: Session, authorization: str, limit: int, offset: int, status: Optional[str] = None
) -> Dict[str, Any]:
    user = get_user_by_token(authorization, db)

    query = db.query(Order).filter(Order.user_id == user.id)

    if status:
        query = query.filter(Order.status == status)

    total_orders = query.count()

    total_pages = math.ceil(total_orders / limit)

    current_page = (offset // limit) + 1

    orders = query.offset(offset).limit(limit).all()

    order_responses = []
    for order in orders:
        order_date_str = order.order_date.isoformat()

        products_with_quantity = (
            db.query(Product, order_product_table.c.quantity)
            .join(order_product_table, Product.id == order_product_table.c.product_id)
            .filter(order_product_table.c.order_id == order.id)
            .all()
        )

        product_responses = [
            OrderProductResponse(product_id=product.id, quantity=quantity)
            for product, quantity in products_with_quantity
        ]

        order_responses.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                order_date=order_date_str,
                status=order.status,
                products=product_responses,
            )
        )

    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "orders": order_responses,
    }



def get_all_orders(
    db: Session, authorization: str, limit: int, offset: int
) -> List[OrderResponse]:
    user = get_user_by_token(authorization, db)
    check_admin_privileges(user)

    orders_query = db.query(Order).offset(offset).limit(limit)
    orders = orders_query.all()

    order_responses = []
    for order in orders:
        order_date_str = order.order_date.isoformat()

        products_with_quantity = (
            db.query(Product, order_product_table.c.quantity)
            .join(
                order_product_table,
                Product.id == order_product_table.c.product_id,
            )
            .filter(order_product_table.c.order_id == order.id)
            .all()
        )

        product_responses = [
            OrderProductResponse(product_id=product.id, quantity=quantity)
            for product, quantity in products_with_quantity
        ]

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
    order_data: OrderUpdate,
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

    if order_data.status is not None:
        order.status = order_data.status

    db.commit()
    db.refresh(order)

    order_date_str = order.order_date.isoformat()

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

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        order_date=order_date_str,
        status=order.status,
        products=product_responses,
    )


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
