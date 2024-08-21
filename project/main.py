from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.dto import EmailStr
from jwt_token import verify_refresh_token
from utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_user_by_email,
    set_jwt_cookie,
    remove_jwt_cookie,
    hash_password,
)
from database.database import get_db
from database.tables import User

app = FastAPI()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginFrom(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: LoginFrom = Depends(),
    db: Session = Depends(get_db),
    response: Response = Response(),
):
    user = get_user_by_email(db, form_data.email)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )

    set_jwt_cookie(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token_auth(
    response: Response,
    refresh_token: str = Cookie(
        None
    ),  # Automatically reads the refresh token from cookies
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        token_data = verify_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(
        data={"sub": token_data["sub"], "user_id": token_data["user_id"]}
    )
    set_jwt_cookie(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@app.post("/auth/logout")
async def logout(response: Response):
    remove_jwt_cookie(response)
    return {"msg": "Successfully logged out"}


@app.post("/auth/register", response_model=UserCreate)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User).filter(User.email == user_data.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserCreate(
        username=new_user.username,
        email=new_user.email,
        password=user_data.password,
    )
