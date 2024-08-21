from passlib.context import CryptContext
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from database.tables import User
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()
