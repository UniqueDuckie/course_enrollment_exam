from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Course
from app.repository import course as course_repo
from app.schemas.course import CourseCreate, CourseUpdate


def get_or_404(db: Session, course_id: int) -> Course:
    course = course_repo.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


def create(db: Session, data: CourseCreate) -> Course:
    if course_repo.find_by_code(db, data.code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Course code already exists"
        )
    try:
        return course_repo.create(
            db, title=data.title, code=data.code, capacity=data.capacity
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Course code already exists"
        )


def update(db: Session, course_id: int, data: CourseUpdate) -> Course:
    course = get_or_404(db, course_id)
    if data.code is not None and data.code != course.code:
        if course_repo.find_by_code(db, data.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course code already exists",
            )
    try:
        return course_repo.update(
            db, course, title=data.title, code=data.code, capacity=data.capacity
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Course code already exists"
        )


def activate(db: Session, course_id: int) -> Course:
    course = get_or_404(db, course_id)
    return course_repo.activate(db, course)


def deactivate(db: Session, course_id: int) -> Course:
    course = get_or_404(db, course_id)
    return course_repo.deactivate(db, course)


def delete(db: Session, course_id: int) -> None:
    course = get_or_404(db, course_id)
    course_repo.soft_delete(db, course)
