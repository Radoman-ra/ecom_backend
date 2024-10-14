from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from tqdm.asyncio import tqdm
from ..tables import Order, User, Product
import random

fake = Faker()


async def seed_orders(db: Session, num_orders: int):
    users_query = db.query(User).all()
    products_query = db.query(Product).all()

    users = [user.id for user in users_query]
    products = [product.id for product in products_query]

    order_products_batch = []

    async for _ in tqdm(range(num_orders), desc="Seeding Orders"):
        order = Order(
            user_id=fake.random_element(elements=users),
            status=fake.random_element(
                elements=["pending", "shipped", "delivered", "cancelled"]
            ),
        )
        db.add(order)
        db.flush()

        num_products = fake.random_int(min=1, max=5)
        order_products = random.sample(
            products, min(num_products, len(products))
        )

        for product_id in order_products:
            order_products_batch.append(
                {
                    "order_id": order.id,
                    "product_id": product_id,
                    "quantity": fake.random_number(digits=2),
                }
            )

        if len(order_products_batch) >= 100:
            db.execute(
                text(
                    "INSERT INTO order_product (order_id, product_id, quantity) VALUES (:order_id, :product_id, :quantity)"
                ),
                order_products_batch,
            )
            db.commit()
            order_products_batch = []

    if order_products_batch:
        db.execute(
            text(
                "INSERT INTO order_product (order_id, product_id, quantity) VALUES (:order_id, :product_id, :quantity)"
            ),
            order_products_batch,
        )
        db.commit()
