import os
import uuid
from fastapi import HTTPException, Response, status, UploadFile, Depends
from sqlalchemy.orm import Session
from app.database.tables import User
from app.core.security import get_user_by_token
from pathlib import Path
from shutil import copyfileobj
import imghdr

AVATAR_FOLDER = Path(__file__).resolve().parent.parent.parent / "static" / "avatars"

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

random_hash = uuid.uuid4().hex

def create_avatar_file_path(user_id: int, file_extension: str):
    return AVATAR_FOLDER / f"{user_id}.{file_extension}"

def validate_image(file: UploadFile):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    image_type = imghdr.what(file.file)
    if image_type not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type."
        )
    return file_extension

async def upload_user_avatar(file: UploadFile, db: Session, authorization: str):
    user = get_user_by_token(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    file_extension = validate_image(file)

    avatar_path = AVATAR_FOLDER / f"{random_hash}.{file_extension}"
    AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)

    with avatar_path.open("wb") as buffer:
        file.file.seek(0)
        copyfileobj(file.file, buffer)
    
    avatar_url = f"{random_hash}.{file_extension}"
    user.avatar_path = avatar_url
    db.commit()
    
    return {"msg": "Avatar uploaded successfully", "avatar_url": avatar_url}


async def get_user_avatar(db: Session, authorization: str):

    user = get_user_by_token(authorization, db)

    if not user or not user.avatar_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )

    avatar_file_path = AVATAR_FOLDER / f"{user.avatar_path}"
    print(avatar_file_path)
    if not avatar_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar file does not exist"
        )

    return {"avatar_url": user.avatar_path}


async def delete_user_avatar(db: Session, authorization: str):

    user = get_user_by_token(authorization, db)

    if not user or not user.avatar_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )

    avatar_file_path = Path(user.avatar_path)
    if avatar_file_path.exists():
        avatar_file_path.unlink()

    user.avatar_path = None
    db.commit()

    return {"msg": "Avatar deleted successfully"}
