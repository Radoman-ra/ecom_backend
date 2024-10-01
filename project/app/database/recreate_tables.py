from database.database import Base, root_engine
from database.tables import *
from project.app.database.create_tables import create_tables


def drop_tables():
    print("drop_tables...")
    Base.metadata.drop_all(bind=root_engine)


if __name__ == "__main__":
    drop_tables()
    create_tables()
    print("done!")
