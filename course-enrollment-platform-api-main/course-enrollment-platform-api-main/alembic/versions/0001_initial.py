"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-01
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _create_user_role_type() -> sa.Enum:
    user_role = sa.Enum("student", "admin", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)
    return user_role


def _create_users_table(user_role: sa.Enum) -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def _create_courses_table() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.CheckConstraint("capacity > 0", name="ck_courses_capacity_positive"),
    )
    op.create_index("ix_courses_code", "courses", ["code"], unique=True)


def _create_enrollments_table() -> None:
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Integer,
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id", "course_id", name="uq_enrollment_user_course"
        ),
    )
    op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])


def upgrade() -> None:
    user_role = _create_user_role_type()
    _create_users_table(user_role)
    _create_courses_table()
    _create_enrollments_table()


def downgrade() -> None:
    op.drop_index("ix_enrollments_course_id", table_name="enrollments")
    op.drop_index("ix_enrollments_user_id", table_name="enrollments")
    op.drop_table("enrollments")
    op.drop_index("ix_courses_code", table_name="courses")
    op.drop_table("courses")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
