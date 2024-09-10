from faker import Faker
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm
from ..tables import Product, Category, Supplier

fake = Faker()


async def seed_products(db: Session, num_products: int):
    categories = db.query(Category).all()
    suppliers = db.query(Supplier).all()

    fake.unique.clear()
    used_names = set()

    async for _ in tqdm(range(num_products), desc="Seeding Products"):
        name = fake.unique.word()

        while name in used_names:
            name = fake.unique.word()

        used_names.add(name)

        product = Product(
            name=name,
            description=fake.text(max_nb_chars=500),
            price=fake.random_number(digits=3),
            category_id=fake.random_element(
                elements=[c.id for c in categories]
            ),
            supplier_id=fake.random_element(
                elements=[s.id for s in suppliers]
            ),
            quantity=fake.random_number(digits=2),
        )
        db.add(product)

    db.commit()
