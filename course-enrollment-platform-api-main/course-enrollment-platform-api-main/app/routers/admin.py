from typing import List

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models import User
from app.repository import audit_log as audit_repo
from app.repository import enrollment as enrollment_repo
from app.schemas.audit_log import AuditLogOut
from app.schemas.enrollment import EnrollmentOut
from app.services import course as course_service
from app.services import enrollment as enrollment_service

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/enrollments", response_model=List[EnrollmentOut])
def list_all_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return enrollment_repo.list_all(
        db, skip=skip, limit=limit, include_deleted=include_deleted
    )


@router.get(
    "/courses/{course_id}/enrollments", response_model=List[EnrollmentOut]
)
def list_course_enrollments(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    course_service.get_or_404(db, course_id)
    return enrollment_repo.list_by_course(
        db,
        course_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
    )


@router.delete(
    "/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_enrollment(
    enrollment_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    enrollment_service.admin_remove(db, current_user, enrollment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/audit-logs", response_model=List[AuditLogOut])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return audit_repo.list_all(db, skip=skip, limit=limit)
