from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.content import ContentKind, DifficultyLevel, PublicationStatus


class ContentBase(BaseModel):
    slug: str = Field(..., min_length=3, max_length=120)
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    difficulty: DifficultyLevel = DifficultyLevel.beginner
    estimated_minutes: int = Field(..., ge=1)
    tags: list[str] = Field(default_factory=list)
    status: PublicationStatus = PublicationStatus.published
    author: str = Field(..., min_length=2, max_length=120)


class ContentCreate(ContentBase):
    body_markdown: str = Field(default="", description="Long-form markdown body.")


class ContentUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=3, max_length=120)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    body_markdown: str | None = None
    difficulty: DifficultyLevel | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    tags: list[str] | None = None
    status: PublicationStatus | None = None
    author: str | None = Field(default=None, min_length=2, max_length=120)


class ContentSummaryRead(ContentBase):
    id: int
    content_type: ContentKind
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentDetailRead(ContentSummaryRead):
    body_markdown: str
