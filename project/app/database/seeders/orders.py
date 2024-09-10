from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from tqdm.asyncio import tqdm
from ..tables import Order, User, Product

fake = Faker()

async def seed_orders(db: Session, num_orders: int):
    users = db.query(User).all()
    products = db.query(Product).all()

    async for _ in tqdm(range(num_orders), desc="Seeding Orders"):
        order = Order(
            user_id=fake.random_element(elements=[u.id for u in users]),
            status=fake.random_element(
                elements=["Pending", "Shipped", "Delivered", "Cancelled"]
            ),
        )
        db.add(order)
        db.commit()

        order_products = fake.random_elements(
            elements=[p.id for p in products],
            unique=True,
            length=fake.random_int(min=1, max=5),
        )

        sql = text(
            "INSERT INTO order_product (order_id, product_id, quantity) VALUES (:order_id, :product_id, :quantity)"
        )

        for product_id in order_products:
            db.execute(
                sql,
                {
                    "order_id": order.id,
                    "product_id": product_id,
                    "quantity": fake.random_number(digits=2),
                },
            )

        db.commit()
