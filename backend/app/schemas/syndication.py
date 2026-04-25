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
    total: int = Field(..., description="Total number of items matching this query across all pages.")
    generated_at: datetime = Field(..., description="Server timestamp when the feed was generated.")
    limit: int = Field(..., description="Maximum number of items returned in this page.")
    offset: int = Field(..., description="Zero-based index of the first item in this page.")
    has_more: bool = Field(..., description="True if more items exist beyond this page.")


class FeedResponse(BaseModel):
    meta: FeedMeta
    items: list[FeedItem]


class FeedItemDetail(FeedItem):
    """Detail-friendly syndication payload for a single published content item.

    Superset of ``FeedItem`` — same stable identifier (``content_type`` + ``slug``),
    same public fields, plus the long-form markdown body.
    """

    body_markdown: str


class LearningPathFeedStep(BaseModel):
    """A single ordered step within a syndicated learning path.

    Reference-only: partners follow up via ``/syndication/content/{content_type}/{slug}``
    for full per-step detail.
    """

    position: int
    content_type: ContentKind
    slug: str
    title: str

    model_config = ConfigDict(from_attributes=True)


class LearningPathFeedDetail(BaseModel):
    """Public syndication payload for one published learning path.

    A learning path is exposed iff it has at least one step whose underlying
    content is ``status = published``. Unpublished or orphaned steps are filtered
    out; original ``position`` values are preserved (gaps are intentional).
    """

    slug: str
    title: str
    description: str
    step_count: int = Field(..., description="Number of published steps after filtering.")
    estimated_minutes_total: int = Field(..., description="Sum of estimated minutes across published steps.")
    created_at: datetime
    updated_at: datetime
    steps: list[LearningPathFeedStep]

    model_config = ConfigDict(from_attributes=True)
