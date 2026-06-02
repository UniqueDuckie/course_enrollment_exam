from typing import List

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.repository import course as course_repo
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate
from app.services import course as course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[CourseOut])
def list_active_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return course_repo.list_active(db, skip=skip, limit=limit)


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.get_or_404(db, course_id)


@router.post(
    "",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    return course_service.create(db, payload)


@router.put(
    "/{course_id}",
    response_model=CourseOut,
    dependencies=[Depends(require_admin)],
)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    return course_service.update(db, course_id, payload)


@router.patch(
    "/{course_id}/activate",
    response_model=CourseOut,
    dependencies=[Depends(require_admin)],
)
def activate_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.activate(db, course_id)


@router.patch(
    "/{course_id}/deactivate",
    response_model=CourseOut,
    dependencies=[Depends(require_admin)],
)
def deactivate_course(course_id: int, db: Session = Depends(get_db)):
    return course_service.deactivate(db, course_id)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course_service.delete(db, course_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
