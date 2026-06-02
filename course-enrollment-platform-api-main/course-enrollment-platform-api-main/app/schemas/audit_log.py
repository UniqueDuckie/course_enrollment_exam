from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import AuditAction, UserRole


class AuditLogOut(BaseModel):
    id: int
    action: AuditAction
    enrollment_id: Optional[int]
    user_id: Optional[int]
    course_id: Optional[int]
    actor_id: Optional[int]
    actor_role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
