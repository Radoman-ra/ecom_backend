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
<<<<<<< HEAD
import requests
=======
>>>>>>> main

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

<<<<<<< HEAD
=======

def create_avatar_file_path(user_id: int, file_extension: str):
    return AVATAR_FOLDER / f"{user_id}.{file_extension}"

>>>>>>> main
def login_via_google(request: Request):
    print("login_via_google called")
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    print(f"Redirect URI: {redirect_uri}")
    return oauth.google.authorize_redirect(request, redirect_uri)

<<<<<<< HEAD
def validate_and_save_avatar(avatar_url: str):
    print(f"validate_and_save_avatar called with avatar_url: {avatar_url}")
=======
def validate_and_save_avatar(avatar_url: str, user_id: int):
>>>>>>> main
    try:
        response = requests.get(avatar_url)
        response.raise_for_status()

        file_extension = imghdr.what(None, h=response.content)
<<<<<<< HEAD
        print(f"File extension: {file_extension}")
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type."
            )

        AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
        random_hash = uuid.uuid4().hex
        avatar_filename = f"{random_hash}.{file_extension}"
        avatar_path = AVATAR_FOLDER / avatar_filename

        with avatar_path.open("wb") as buffer:
            buffer.write(response.content)

        print(f"Avatar saved as: {avatar_filename}")
        return {"msg": "Avatar saved successfully", "avatar_filename": str(avatar_filename)}
    except Exception as e:
        print(f"Error in validate_and_save_avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def handle_google_callback(request: Request, db: Session):
    print("handle_google_callback called")
    try:
        token = await oauth.google.authorize_access_token(request)
        print(f"Token: {token}")
        user_info = await oauth.google.userinfo(token=token)
        print(f"User info: {user_info}")
=======
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )

        avatar_path = create_avatar_file_path(user_id, file_extension)
        AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
        with avatar_path.open("wb") as buffer:
            buffer.write(response.content)

        return f"{user_id}.{file_extension}"
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download avatar from URL"
        )


async def handle_google_callback(request: Request, db: Session):
    try:
        token = await oauth.google.authorize_access_token(request)
        nonce = token.get('userinfo', {}).get('nonce')
        if not nonce:
            raise HTTPException(status_code=400, detail="Missing nonce in token response")
>>>>>>> main

        avatar_filename = None
        avatar_url = user_info.get('picture')
        if avatar_url:
            result = validate_and_save_avatar(avatar_url)
            avatar_filename = result['avatar_filename']

<<<<<<< HEAD
        existing_user = db.query(User).filter(User.email == user_info['email']).first()
        print(f"Existing user: {existing_user}")

=======
        name = user_info.get('name', user_info['email'])
        avatar_url = user_info.get('picture')
        existing_user = get_user_by_email(db, user_info['email'])
>>>>>>> main
        if existing_user:
            if existing_user.user_type != UserType.google:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered with a different method"
                )
<<<<<<< HEAD
            if avatar_filename and existing_user.avatar_path != avatar_filename:
                existing_user.avatar_path = avatar_filename
                db.commit()
        else:
            new_user = User(
                username=user_info.get('email'),
                email=user_info.get('email'),
                user_type=UserType.google,
                avatar_path=avatar_filename
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
        user = get_user_by_email(db, user_info.email)
        access_token = create_access_token(
            data={"sub": user_info.get('email'), "user_id": user.id}
        )
        refresh_token = create_refresh_token(
            data={"sub": user_info.get('email'), "user_id": user.id}
        )

        frontend_url = os.getenv("FRONTEND_URL")
        redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        print(f"Redirect URL: {redirect_url}")
=======
        else:
            user = User(
                username=name,
                email=user_info['email'],
                password_hash=None,
                user_type=UserType.google
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        user = existing_user

        if not user.avatar_path:
            user.avatar_path = validate_and_save_avatar(avatar_url, user.id)
            db.commit()

        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

        frontend_callback_url = os.getenv("FRONTEND_URL") + "/auth/callback"
        redirect_url = f"{frontend_callback_url}?access_token={access_token}&refresh_token={refresh_token}"
>>>>>>> main
        return RedirectResponse(redirect_url)

    except HTTPException as e:
        print(f"HTTPException in handle_google_callback: {e}")
        raise e
<<<<<<< HEAD
    except Exception as e:
        print(f"Exception in handle_google_callback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Google OAuth callback failed"
        )
=======
    except Exception:
        raise HTTPException(status_code=500, detail="Google OAuth callback failed")
>>>>>>> main

def login_user(form_data: LoginFrom, db: Session, response: Response):
    print(f"login_user called with form_data: {form_data}")
    user = get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.password_hash):
        print("Invalid credentials")
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

    print(f"Access token: {access_token}, Refresh token: {refresh_token}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

def refresh_access_token(response: Response, refresh_token: str, db: Session):
    print(f"refresh_access_token called with refresh_token: {refresh_token}")
    if not refresh_token:
        print("Refresh token missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        token_data = verify_refresh_token(refresh_token)
        print(f"Token data: {token_data}")
    except Exception:
        print("Invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(
        data={"sub": token_data["sub"], "user_id": token_data["user_id"]}
    )
    set_jwt_cookie(response, access_token, refresh_token)

    print(f"New access token: {access_token}")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

def logout_user(response: Response, authorization: str):
    print("logout_user called")
    remove_jwt_cookie(response)
    return {"msg": "Successfully logged out"}

def register_new_user(user_data: UserCreate, db: Session):
    print(f"register_new_user called with user_data: {user_data}")
    existing_user = (
        db.query(User).filter(User.email == user_data.email).first()
    )
    if existing_user:
        print("Email already registered")
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

    print(f"New user registered: {new_user}")
    return UserCreate(
        username=new_user.username,
        email=new_user.email,
        password=user_data.password,
    )