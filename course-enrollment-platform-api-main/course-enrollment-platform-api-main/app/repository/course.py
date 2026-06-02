from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Course


def list_active(db: Session, *, skip: int = 0, limit: int = 100) -> List[Course]:
    return (
        db.query(Course)
        .filter(Course.is_active, Course.deleted_at.is_(None))
        .order_by(Course.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_id(db: Session, course_id: int) -> Optional[Course]:
    return (
        db.query(Course)
        .filter(Course.id == course_id, Course.deleted_at.is_(None))
        .first()
    )


def find_by_code(db: Session, code: str) -> Optional[Course]:
    return db.query(Course).filter(Course.code == code).first()


def create(db: Session, *, title: str, code: str, capacity: int) -> Course:
    course = Course(title=title, code=code, capacity=capacity, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update(
    db: Session,
    course: Course,
    *,
    title: Optional[str] = None,
    code: Optional[str] = None,
    capacity: Optional[int] = None,
) -> Course:
    if title is not None:
        course.title = title
    if code is not None:
        course.code = code
    if capacity is not None:
        course.capacity = capacity
    db.commit()
    db.refresh(course)
    return course


def activate(db: Session, course: Course) -> Course:
    course.is_active = True
    db.commit()
    db.refresh(course)
    return course


def deactivate(db: Session, course: Course) -> Course:
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course


def soft_delete(db: Session, course: Course) -> None:
    course.deleted_at = datetime.now(timezone.utc)
    course.is_active = False
    db.commit()
