from fastapi import APIRouter, Depends, Header, Request, Response
from sqlalchemy.orm import Session
from app.schemas.schemas import TokenResponse, UserCreate, LoginFrom, UserInfo
from app.database.database import get_db
from app.controllers.auth_controller import (
    handle_google_callback,
    login_user,
    login_via_google,
    logout_user,
    refresh_access_token,
    register_new_user,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/login/google")
async def login_with_google(request: Request):
    return await login_via_google(request)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    return await handle_google_callback(request, db)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: LoginFrom,
    db: Session = Depends(get_db),
    response: Response = Response(),
):
    return  login_user(form_data, db, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_auth(
    response: Response,
    refresh_token: str,
    db: Session = Depends(get_db),
):
    return  refresh_access_token(response, refresh_token, db)


@router.post(
    "/logout",
    summary="Logout User",
    response_description="Successfully logged out",
)
async def logout(response: Response, authorization: str = Header(None)):
    return  logout_user(response, authorization)


@router.post("/register", response_model=UserCreate)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return  register_new_user(user_data, db)
