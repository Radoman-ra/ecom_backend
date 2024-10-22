from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    set_jwt_cookie,
    remove_jwt_cookie,
)
from app.schemas.schemas import TokenResponse, TokenResponseGoogle, UserCreate, LoginFrom
from app.database.tables import User, UserType
from app.utils.utils import (
    verify_password,
    get_user_by_email,
    hash_password,
)
from app.core.security import verify_refresh_token
from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)


def login_via_google(request: Request):
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    return oauth.google.authorize_redirect(request, redirect_uri)

import os
from fastapi import HTTPException, status, Response
from fastapi.responses import RedirectResponse

async def handle_google_callback(request: Request, db: Session, response: Response):
    try:
        token = await oauth.google.authorize_access_token(request)
        
        nonce = token.get('userinfo', {}).get('nonce')
        if not nonce:
            raise HTTPException(status_code=400, detail="Missing nonce in token response")

        user_info = await oauth.google.parse_id_token(token, nonce=nonce)

        name = user_info.get('name')
        if not name:
            name = user_info['email']

        user = get_user_by_email(db, user_info['email'])

        if not user:
            user = User(
                username=name,
                email=user_info['email'],
                password_hash=None,
                user_type=UserType.google
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

        set_jwt_cookie(response, access_token, refresh_token)

        frontend_url = os.getenv("FRONTEND_URL")
        return RedirectResponse(frontend_url)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Google OAuth callback failed")


def login_user(form_data: LoginFrom, db: Session, response: Response):
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

    # set_jwt_cookie(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def refresh_access_token(response: Response, refresh_token: str, db: Session):
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


def logout_user(response: Response, authorization: str):
    remove_jwt_cookie(response)
    return {"msg": "Successfully logged out"}


def register_new_user(user_data: UserCreate, db: Session):
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
