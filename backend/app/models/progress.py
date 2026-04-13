"""ContentProgress model.

Tracks per-user progress on content items.

Loose foreign key note: courses, tutorials, and labs live in separate
parallel tables (see Architecture.md, content modeling approach), so a
DB-level foreign key on content_id is not possible. The progress service
is responsible for validating (content_type, content_id) pairs.

If a future slice adds content deletion, it MUST explicitly delete matching
content_progress rows — the database cannot cascade them for us.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgressState(str, Enum):
    in_progress = "in_progress"
    completed = "completed"


class ContentProgress(Base):
    __tablename__ = "content_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_type",
            "content_id",
            name="uq_content_progress_user_content",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(String(40), nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
