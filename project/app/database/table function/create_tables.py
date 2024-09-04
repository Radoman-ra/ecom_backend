import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from ...database.database import Base, root_engine


def create_tables():
    Base.metadata.create_all(bind=root_engine)


if __name__ == "__main__":
    create_tables()
