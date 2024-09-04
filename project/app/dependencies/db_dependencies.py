from typing import Generator

from database.database import SessionLocal, RootSessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_root_db() -> Generator[Session, None, None]:
    db = RootSessionLocal()
    try:
        yield db
    finally:
        db.close()
