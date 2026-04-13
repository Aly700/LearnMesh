"""baseline phase 2 schema

Revision ID: 0001_baseline_phase_2
Revises:
Create Date: 2026-04-11

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_baseline_phase_2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


CONTENT_TABLES = ("courses", "tutorials", "labs")


def _create_content_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("content_type", sa.String(length=40), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(f"ix_{name}_id", name, ["id"], unique=False)
    op.create_index(f"ix_{name}_slug", name, ["slug"], unique=True)


def _drop_content_table(name: str) -> None:
    op.drop_index(f"ix_{name}_slug", table_name=name)
    op.drop_index(f"ix_{name}_id", table_name=name)
    op.drop_table(name)


def upgrade() -> None:
    for name in CONTENT_TABLES:
        _create_content_table(name)

    op.create_table(
        "learning_paths",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_learning_paths_id", "learning_paths", ["id"], unique=False)
    op.create_index("ix_learning_paths_slug", "learning_paths", ["slug"], unique=True)

    op.create_table(
        "learning_path_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("learning_path_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=40), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("content_slug", sa.String(length=120), nullable=False),
        sa.Column("content_title", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["learning_path_id"],
            ["learning_paths.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("learning_path_id", "position"),
    )
    op.create_index(
        "ix_learning_path_items_id",
        "learning_path_items",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_learning_path_items_learning_path_id",
        "learning_path_items",
        ["learning_path_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learning_path_items_learning_path_id",
        table_name="learning_path_items",
    )
    op.drop_index("ix_learning_path_items_id", table_name="learning_path_items")
    op.drop_table("learning_path_items")

    op.drop_index("ix_learning_paths_slug", table_name="learning_paths")
    op.drop_index("ix_learning_paths_id", table_name="learning_paths")
    op.drop_table("learning_paths")

    for name in reversed(CONTENT_TABLES):
        _drop_content_table(name)
