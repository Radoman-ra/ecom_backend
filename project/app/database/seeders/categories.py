from faker import Faker
from sqlalchemy.orm import Session
from tqdm import tqdm
from ..tables import Category

fake = Faker()


async def seed_categories(db: Session, num_categories: int):
    used_names = set()

    for _ in tqdm(range(num_categories), desc="Seeding Categories"):
        base_name = fake.word()
        name = base_name
        counter = 1

        while name in used_names:
            name = f"{base_name}{counter}"
            counter += 1

        used_names.add(name)

        category = Category(name=name, description=fake.text(max_nb_chars=200))
        db.add(category)

    db.commit()
