from faker import Faker
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm
from ..tables import Category

fake = Faker()


async def seed_categories(db: Session, num_categories: int):
    fake.unique.clear()
    used_names = set()

    async for _ in tqdm(range(num_categories), desc="Seeding Categories"):
        name = fake.word()

        while name in used_names:
            name = fake.word()

        used_names.add(name)

        category = Category(name=name, description=fake.text(max_nb_chars=200))
        db.add(category)

    db.commit()
