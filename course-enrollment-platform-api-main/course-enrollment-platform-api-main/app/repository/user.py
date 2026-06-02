from typing import Optional

from sqlalchemy.orm import Session

from app.models import User, UserRole


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create(
    db: Session,
    *,
    name: str,
    email: str,
    hashed_password: str,
    role: UserRole,
) -> User:
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
