from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.dto import User
from utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_user_by_email,
    set_jwt_cookie,
    remove_jwt_cookie,
    verify_refresh_token,
)
from database.database import get_db

app = FastAPI()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
    set_jwt_cookie(response, access_token, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response, refresh_token: str = Cookie(None), db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    try:
        token_data = verify_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    access_token = create_access_token(
        data={"sub": token_data["sub"], "user_id": token_data["user_id"]}
    )
    set_jwt_cookie(response, access_token, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/logout")
async def logout(response: Response):
    remove_jwt_cookie(response)
    return {"msg": "Successfully logged out"}
