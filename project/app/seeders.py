import asyncio
import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.seeders.categories import seed_categories
from database.seeders.suppliers import seed_suppliers
from database.seeders.products import seed_products
from database.seeders.orders import seed_orders
from database.tables import (
    Category,
    Supplier,
    Product,
    Order,
)
from database.database import SessionLocal


async def clear_db(db: Session):
    db.execute(text("DELETE FROM order_product"))
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(Supplier).delete()
    db.commit()
    print("Database cleared")


async def seed():
    start_time = time.time()
    db = SessionLocal()
    try:
        await clear_db(db)
        await seed_suppliers(db, 10000)
        await seed_categories(db, 10000)
        await seed_products(db, 200000)
        await seed_orders(db, 10000)
    finally:
        db.close()

    elapsed_time = time.time() - start_time
    print(f"Seeding completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(seed())
