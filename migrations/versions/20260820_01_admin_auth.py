"""Add admin users, server-side auth sessions, and security audit events.

Revision ID: 20260820_01
Revises:
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20260820_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320, collation="NOCASE"), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "auth_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("auth_session") as batch_op:
        batch_op.create_index("ix_auth_session_admin_user_id", ["admin_user_id"])
        batch_op.create_index("ix_auth_session_expires_at", ["expires_at"])
        batch_op.create_index("ix_auth_session_token_hash", ["token_hash"], unique=True)

    op.create_table(
        "security_audit_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("security_audit_event") as batch_op:
        batch_op.create_index("ix_security_audit_event_admin_user_id", ["admin_user_id"])
        batch_op.create_index(
            "ix_security_audit_rate_limit",
            ["source_hash", "event_type", "created_at"],
        )


def downgrade():
    with op.batch_alter_table("security_audit_event") as batch_op:
        batch_op.drop_index("ix_security_audit_rate_limit")
        batch_op.drop_index("ix_security_audit_event_admin_user_id")
    op.drop_table("security_audit_event")

    with op.batch_alter_table("auth_session") as batch_op:
        batch_op.drop_index("ix_auth_session_token_hash")
        batch_op.drop_index("ix_auth_session_expires_at")
        batch_op.drop_index("ix_auth_session_admin_user_id")
    op.drop_table("auth_session")
    op.drop_table("admin_user")
