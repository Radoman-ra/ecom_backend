import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

MYSQL_ROOT_PASSWORD= "qwerty"
MYSQL_DATABASE= "ecommerce_product_api"
MYSQL_USER= "mysql"
MYSQL_PASSWORD= "q1w2e3e3w2q1"
MYSQL_HOST= "db"
MYSQL_PORT= 3306

# MYSQL_USER = os.getenv("MYSQL_USER")
# MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
# MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
# MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
# MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
# MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
print(SQLALCHEMY_DATABASE_URL)
SQLALCHEMY_ROOT_DATABASE_URL = f"mysql+pymysql://root:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
root_engine = create_engine(SQLALCHEMY_ROOT_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
RootSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=root_engine)

Base = declarative_base()


def get_db():
    print(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_ROOT_PASSWORD)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_root_db():
    print(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_ROOT_PASSWORD)
    root_db = RootSessionLocal()
    try:
        yield root_db
    finally:
        root_db.close()
