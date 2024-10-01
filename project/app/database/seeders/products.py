from faker import Faker
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm
from ..tables import Product, Category, Supplier

fake = Faker()

async def seed_products(
    db: Session, num_products: int, batch_size: int = 1000
):
    categories = db.query(Category).all()
    suppliers = db.query(Supplier).all()

    category_ids = [c.id for c in categories]
    supplier_ids = [s.id for s in suppliers]
    products_to_add = []
    
    name_count = {}

    async for _ in tqdm(range(num_products), desc="Seeding Products"):
        base_name = fake.word()

        if base_name in name_count:
            name_count[base_name] += 1
            product_name = f"{base_name}{name_count[base_name]}"
        else:
            name_count[base_name] = 1
            product_name = base_name

        product = Product(
            name=product_name,
            description=fake.text(max_nb_chars=500),
            price=fake.random_number(digits=3),
            category_id=fake.random_element(elements=category_ids),
            supplier_id=fake.random_element(elements=supplier_ids),
            quantity=fake.random_number(digits=2),
        )
        products_to_add.append(product)

        if len(products_to_add) >= batch_size:
            db.bulk_save_objects(products_to_add)
            db.commit()
            products_to_add = []

    if products_to_add:
        db.bulk_save_objects(products_to_add)
        db.commit()
