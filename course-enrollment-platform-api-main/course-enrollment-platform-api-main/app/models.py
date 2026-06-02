import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class AuditAction(str, enum.Enum):
    enrolled = "enrolled"
    deregistered = "deregistered"
    admin_removed = "admin_removed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole, name="user_role"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    enrollments = relationship(
        "Enrollment", back_populates="user", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    enrollments = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_courses_capacity_positive"),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id = Column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )


class EnrollmentAuditLog(Base):
    __tablename__ = "enrollment_audit_logs"

    id = Column(Integer, primary_key=True)
    action = Column(SAEnum(AuditAction, name="audit_action"), nullable=False)
    enrollment_id = Column(
        Integer,
        ForeignKey("enrollments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_role = Column(SAEnum(UserRole, name="user_role"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
