import os
from fastapi import HTTPException, status, UploadFile, Response
from sqlalchemy.orm import Session
from app.database.tables import User
from ..utils.utils import get_user_by_email
from app.core.security import get_user_by_token, verify_access_token
from pathlib import Path
from shutil import copyfileobj

AVATAR_FOLDER = Path(__file__).resolve().parent.parent / "static" / "avatars"

def create_avatar_file_path(user_id: int, filename: str):
    file_extension = filename.split(".")[-1]
    return AVATAR_FOLDER / f"{user_id}.{file_extension}"


async def upload_user_avatar(file: UploadFile, db: Session, authorization: str):

    user = get_user_by_token(authorization, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    avatar_path = create_avatar_file_path(user.id, file.filename)

    AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
    with avatar_path.open("wb") as buffer:
        copyfileobj(file.file, buffer)

    avatar_url = f"/static/avatars/{user.id}.{file.filename.split('.')[-1]}"
    user.avatar_path = avatar_url
    db.commit()
    db.refresh(user)

    return {"msg": "Avatar uploaded successfully", "avatar_url": avatar_url}



async def get_user_avatar(db: Session, authorization: str):

    user = get_user_by_token(authorization, db)

    if not user or not user.avatar_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )

    avatar_file_path = Path(user.avatar_path)
    if not avatar_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar file does not exist"
        )

    return Response(content=avatar_file_path.read_bytes(), media_type="image/jpeg")



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
