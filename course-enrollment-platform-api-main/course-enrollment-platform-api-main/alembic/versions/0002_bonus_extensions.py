"""bonus extensions: soft deletes + audit log

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01
"""
from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _add_soft_delete_columns() -> None:
    op.add_column(
        "courses",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "enrollments",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def _create_audit_action_type() -> sa.Enum:
    audit_action = sa.Enum(
        "enrolled", "deregistered", "admin_removed", name="audit_action"
    )
    audit_action.create(op.get_bind(), checkfirst=True)
    return audit_action


def _create_audit_log_table(audit_action: sa.Enum) -> None:
    op.create_table(
        "enrollment_audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("action", audit_action, nullable=False),
        sa.Column(
            "enrollment_id",
            sa.Integer,
            sa.ForeignKey("enrollments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "course_id",
            sa.Integer,
            sa.ForeignKey("courses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "actor_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "actor_role",
            sa.Enum("student", "admin", name="user_role", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_audit_enrollment_id", "enrollment_audit_logs", ["enrollment_id"]
    )
    op.create_index("ix_audit_user_id", "enrollment_audit_logs", ["user_id"])
    op.create_index(
        "ix_audit_course_id", "enrollment_audit_logs", ["course_id"]
    )


def upgrade() -> None:
    _add_soft_delete_columns()
    audit_action = _create_audit_action_type()
    _create_audit_log_table(audit_action)


def downgrade() -> None:
    op.drop_index("ix_audit_course_id", table_name="enrollment_audit_logs")
    op.drop_index("ix_audit_user_id", table_name="enrollment_audit_logs")
    op.drop_index("ix_audit_enrollment_id", table_name="enrollment_audit_logs")
    op.drop_table("enrollment_audit_logs")
    sa.Enum(name="audit_action").drop(op.get_bind(), checkfirst=True)
    op.drop_column("enrollments", "deleted_at")
    op.drop_column("courses", "deleted_at")
