from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import AuditAction, EnrollmentAuditLog, User


@dataclass
class EnrollmentRef:
    user_id: int
    course_id: int
    enrollment_id: Optional[int] = None


def record(
    db: Session,
    *,
    action: AuditAction,
    actor: User,
    ref: EnrollmentRef,
) -> EnrollmentAuditLog:
    entry = EnrollmentAuditLog(
        action=action,
        actor_id=actor.id,
        actor_role=actor.role,
        user_id=ref.user_id,
        course_id=ref.course_id,
        enrollment_id=ref.enrollment_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_all(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[EnrollmentAuditLog]:
    return (
        db.query(EnrollmentAuditLog)
        .order_by(EnrollmentAuditLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
