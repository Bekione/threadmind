"""initial schema

Revision ID: 0001_init
Revises: 
Create Date: 2025-11-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", sa.String(length=255), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("pending", "processing", "failed", "done", name="jobstatus"), nullable=False, server_default="pending"),
        sa.Column("summary", sa.Text()),
        sa.Column("highlights", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("token_usage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost", sa.Numeric(10, 4)),
    )

    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
