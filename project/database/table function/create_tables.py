from database.tables import User, Supplier, Category, Product, Order
from database.database import Base, root_engine


def create_tables():
    Base.metadata.create_all(bind=root_engine)


if __name__ == "__main__":
    create_tables()
