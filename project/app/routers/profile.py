from fastapi import APIRouter, Depends, UploadFile, File, Response, Header
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.controllers.profile_controller import (
    upload_user_avatar,
    get_user_avatar,
    delete_user_avatar
)

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.post("/avatar/upload")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    return await upload_user_avatar(file, db, authorization)

@router.get("/avatar")
async def fetch_avatar(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    return await get_user_avatar(db, authorization)

@router.delete("/avatar")
async def remove_avatar(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    return await delete_user_avatar(db, authorization)
