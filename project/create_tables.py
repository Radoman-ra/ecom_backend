from database.tables import User, Supplier, Category, Product, Order
from database.database import Base, engine


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
