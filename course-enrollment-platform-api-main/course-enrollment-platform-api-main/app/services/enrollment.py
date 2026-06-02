from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AuditAction, Course, Enrollment, User
from app.repository import audit_log as audit_repo
from app.repository import course as course_repo
from app.repository import enrollment as enrollment_repo
from app.repository.audit_log import EnrollmentRef


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = course_repo.get_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


def enroll(db: Session, user: User, course_id: int) -> Enrollment:
    course = _get_course_or_404(db, course_id)
    if not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course is inactive"
        )

    existing = enrollment_repo.find_by_user_and_course(db, user.id, course_id)
    if existing and existing.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this course",
        )

    if enrollment_repo.count_for_course(db, course_id) >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full"
        )

    try:
        enrollment = (
            enrollment_repo.restore(db, existing)
            if existing
            else enrollment_repo.create(db, user_id=user.id, course_id=course_id)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this course",
        )

    audit_repo.record(
        db,
        action=AuditAction.enrolled,
        actor=user,
        ref=EnrollmentRef(
            user_id=user.id,
            course_id=course_id,
            enrollment_id=enrollment.id,
        ),
    )
    return enrollment


def deregister(db: Session, user: User, course_id: int) -> None:
    enrollment = enrollment_repo.find_by_user_and_course(db, user.id, course_id)
    if not enrollment or enrollment.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    enrollment_repo.soft_delete(db, enrollment)
    audit_repo.record(
        db,
        action=AuditAction.deregistered,
        actor=user,
        ref=EnrollmentRef(
            user_id=user.id,
            course_id=course_id,
            enrollment_id=enrollment.id,
        ),
    )


def admin_remove(db: Session, actor: User, enrollment_id: int) -> None:
    enrollment = enrollment_repo.get_by_id(db, enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    user_id = enrollment.user_id
    course_id = enrollment.course_id
    enrollment_repo.soft_delete(db, enrollment)
    audit_repo.record(
        db,
        action=AuditAction.admin_removed,
        actor=actor,
        ref=EnrollmentRef(
            user_id=user_id,
            course_id=course_id,
            enrollment_id=enrollment.id,
        ),
    )
