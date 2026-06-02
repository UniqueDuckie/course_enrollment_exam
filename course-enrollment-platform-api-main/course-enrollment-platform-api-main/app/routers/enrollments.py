from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_student
from app.models import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentOut
from app.services import enrollment as enrollment_service

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll(
    payload: EnrollmentCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    return enrollment_service.enroll(db, current_user, payload.course_id)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def deregister(
    course_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    enrollment_service.deregister(db, current_user, course_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
