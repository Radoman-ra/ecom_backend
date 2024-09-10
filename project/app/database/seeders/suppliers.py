from faker import Faker
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm
from ..tables import Supplier

fake = Faker()


async def seed_suppliers(db: Session, num_suppliers: int):
    fake.unique.clear()

    used_names = set()
    used_emails = set()
    used_phone_numbers = set()

    async for _ in tqdm(range(num_suppliers), desc="Seeding Suppliers"):
        name = fake.unique.company()
        contact_email = fake.unique.email()
        phone_number = fake.unique.numerify("+###########")

        while name in used_names:
            name = fake.unique.company()
        while contact_email in used_emails:
            contact_email = fake.unique.email()
        while phone_number in used_phone_numbers:
            phone_number = fake.unique.numerify("+###########")

        used_names.add(name)
        used_emails.add(contact_email)
        used_phone_numbers.add(phone_number)

        supplier = Supplier(
            name=name,
            contact_email=contact_email,
            phone_number=phone_number,
        )
        db.add(supplier)

    db.commit()
