from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Enrollment


def list_all(
    db: Session, *, skip: int = 0, limit: int = 100, include_deleted: bool = False
) -> List[Enrollment]:
    query = db.query(Enrollment)
    if not include_deleted:
        query = query.filter(Enrollment.deleted_at.is_(None))
    return query.order_by(Enrollment.id).offset(skip).limit(limit).all()


def list_by_course(
    db: Session,
    course_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
) -> List[Enrollment]:
    query = db.query(Enrollment).filter(Enrollment.course_id == course_id)
    if not include_deleted:
        query = query.filter(Enrollment.deleted_at.is_(None))
    return query.order_by(Enrollment.id).offset(skip).limit(limit).all()


def list_by_user(
    db: Session,
    user_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
) -> List[Enrollment]:
    query = db.query(Enrollment).filter(Enrollment.user_id == user_id)
    if not include_deleted:
        query = query.filter(Enrollment.deleted_at.is_(None))
    return query.order_by(Enrollment.id).offset(skip).limit(limit).all()


def get_by_id(db: Session, enrollment_id: int) -> Optional[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.id == enrollment_id, Enrollment.deleted_at.is_(None))
        .first()
    )


def find_by_user_and_course(
    db: Session, user_id: int, course_id: int
) -> Optional[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        .first()
    )


def count_for_course(db: Session, course_id: int) -> int:
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id, Enrollment.deleted_at.is_(None)
        )
        .count()
    )


def create(db: Session, *, user_id: int, course_id: int) -> Enrollment:
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def restore(db: Session, enrollment: Enrollment) -> Enrollment:
    enrollment.deleted_at = None
    enrollment.created_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def soft_delete(db: Session, enrollment: Enrollment) -> None:
    enrollment.deleted_at = datetime.now(timezone.utc)
    db.commit()
