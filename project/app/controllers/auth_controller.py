from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    set_jwt_cookie,
    remove_jwt_cookie,
    verify_refresh_token,
)
from app.schemas.schemas import TokenResponse, TokenResponseGoogle, UserCreate, LoginFrom
from app.database.tables import User, UserType
from app.utils.utils import (
    verify_password,
    get_user_by_email,
    hash_password,
)
from fastapi import HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
import os
from pathlib import Path
import uuid
import imghdr

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

AVATAR_FOLDER = Path(__file__).resolve().parent.parent.parent / "static" / "avatars"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

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


def create_avatar_file_path(user_id: int, file_extension: str) -> Path:
    random_hash = uuid.uuid4().hex
    avatar_filename = f"{random_hash}.{file_extension}"
    avatar_path = AVATAR_FOLDER / avatar_filename
    return avatar_path

def login_via_google(request: Request):
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    return oauth.google.authorize_redirect(request, redirect_uri)

def validate_and_save_avatar(avatar_url: str, user_id: int):
    try:
        response = requests.get(avatar_url)
        response.raise_for_status()

        file_extension = imghdr.what(None, h=response.content)
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type."
            )

        AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
        avatar_path = create_avatar_file_path(user_id, file_extension)
        
        with avatar_path.open("wb") as buffer:
            buffer.write(response.content)
        
        return {"msg": "Avatar saved successfully", "avatar_url": str(avatar_path)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def handle_google_callback(request: Request):
    try:
        token = oauth.google.authorize_access_token(request)
        print(f"Token: {token}")

        nonce = token.get('userinfo', {}).get('nonce')
        if not nonce:
            raise HTTPException(status_code=400, detail="Nonce missing in token")

        user_info = oauth.google.parse_id_token(token, nonce=nonce)
        print(f"User info: {user_info}")

        avatar_url = user_info.get('picture')
        if avatar_url:
            avatar_path = validate_and_save_avatar(avatar_url)
            print(f"Avatar path: {avatar_path}")

        existing_user = db.query(User).filter(User.email == user_info['email']).first()
        print(f"Existing user: {existing_user}")

        if existing_user and existing_user.user_type != UserType.google:
            raise HTTPException(status_code=400, detail="Email already registered with a different method")

        if not existing_user:
            new_user = User(
                username=user_info['name'],
                email=user_info['email'],
                user_type=UserType.google,
                avatar_path=avatar_path
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

        frontend_url = os.getenv("FRONTEND_URL")
        redirect_url = f"{frontend_url}/auth/callback"
        return RedirectResponse(redirect_url)

    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        print(f"Error during Google OAuth callback: {e}")
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