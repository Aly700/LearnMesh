from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class PublicationStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class ContentKind(str, Enum):
    course = "course"
    tutorial = "tutorial"
    lab = "lab"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ContentFieldsMixin(TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    difficulty: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=DifficultyLevel.beginner.value,
    )
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=PublicationStatus.draft.value,
    )
    author: Mapped[str] = mapped_column(String(120), nullable=False)


class Course(ContentFieldsMixin, Base):
    __tablename__ = "courses"

    content_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=ContentKind.course.value,
    )


class Tutorial(ContentFieldsMixin, Base):
    __tablename__ = "tutorials"

    content_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=ContentKind.tutorial.value,
    )


class Lab(ContentFieldsMixin, Base):
    __tablename__ = "labs"

    content_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default=ContentKind.lab.value,
    )
