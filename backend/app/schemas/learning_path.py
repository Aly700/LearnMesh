from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.content import ContentKind, DifficultyLevel, PublicationStatus


class LearningPathContentReferenceBase(BaseModel):
    content_type: ContentKind
    content_id: int = Field(..., ge=1)
    position: int | None = Field(default=None, ge=1)


class LearningPathContentReferenceCreate(LearningPathContentReferenceBase):
    pass


class LearningPathContentReferenceRead(LearningPathContentReferenceBase):
    id: int
    content_slug: str
    content_title: str
    description: str
    difficulty: DifficultyLevel
    estimated_minutes: int
    tags: list[str]
    status: PublicationStatus
    author: str

    model_config = ConfigDict(from_attributes=True)


class LearningPathBase(BaseModel):
    slug: str = Field(..., min_length=3, max_length=120)
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)


class LearningPathCreate(LearningPathBase):
    ordered_content: list[LearningPathContentReferenceCreate] = Field(default_factory=list)


class LearningPathUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=3, max_length=120)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    ordered_content: list[LearningPathContentReferenceCreate] | None = None


class LearningPathRead(LearningPathBase):
    id: int
    step_count: int
    estimated_minutes_total: int
    created_at: datetime
    updated_at: datetime
    ordered_content: list[LearningPathContentReferenceRead]

    model_config = ConfigDict(from_attributes=True)
