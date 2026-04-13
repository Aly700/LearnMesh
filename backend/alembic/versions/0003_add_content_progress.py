"""add content_progress

Revision ID: 0003_add_content_progress
Revises: 0002_add_users
Create Date: 2026-04-11

Notes
-----
content_progress.content_id is a loose reference into the courses, tutorials,
and labs tables. Because those are three separate parallel tables (see
Architecture.md, content modeling approach), no DB-level foreign key on
content_id is possible. Validation is enforced by the progress service.

If a future slice adds content deletion, it MUST explicitly delete matching
content_progress rows — the database cannot cascade them for us.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_add_content_progress"
down_revision: str | Sequence[str] | None = "0002_add_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "content_progress",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=40), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "content_type",
            "content_id",
            name="uq_content_progress_user_content",
        ),
    )
    op.create_index(
        "ix_content_progress_id",
        "content_progress",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_content_progress_user_id",
        "content_progress",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_content_progress_user_id", table_name="content_progress")
    op.drop_index("ix_content_progress_id", table_name="content_progress")
    op.drop_table("content_progress")
