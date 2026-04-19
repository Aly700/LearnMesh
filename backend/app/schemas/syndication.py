from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.content import ContentKind, DifficultyLevel


class FeedItem(BaseModel):
    """A single content item in the syndication feed.

    External consumers should treat ``content_type`` + ``slug`` as the
    stable identifier for a piece of content.
    """

    content_type: ContentKind
    slug: str
    title: str
    description: str
    difficulty: DifficultyLevel
    estimated_minutes: int
    tags: list[str]
    author: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedMeta(BaseModel):
    total: int = Field(..., description="Number of items in this response.")
    generated_at: datetime = Field(..., description="Server timestamp when the feed was generated.")


class FeedResponse(BaseModel):
    meta: FeedMeta
    items: list[FeedItem]


class FeedItemDetail(FeedItem):
    """Detail-friendly syndication payload for a single published content item.

    Superset of ``FeedItem`` — same stable identifier (``content_type`` + ``slug``),
    same public fields, plus the long-form markdown body.
    """

    body_markdown: str
