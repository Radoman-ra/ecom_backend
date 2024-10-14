from app.core.security import decode_access_token
from app.database.tables import User
from app.database.database import get_db
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session


def get_user_by_token(
    authorization: str = Header(None), db: Session = Depends(get_db)
) -> User:
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
