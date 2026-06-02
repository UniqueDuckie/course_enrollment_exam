from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.repository import user as user_repo
from app.schemas.user import UserCreate
from app.security import create_access_token, hash_password, verify_password


def register(db: Session, data: UserCreate) -> User:
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    try:
        return user_repo.create(
            db,
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )


def login(db: Session, *, email: str, password: str) -> str:
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )
    return create_access_token(subject=user.email, role=user.role.value)
