from pydantic import BaseModel, ConfigDict

from app.schemas.content import ContentSummaryRead


class SearchResult(ContentSummaryRead):
    """A ranked search result: a content summary plus relevance metadata."""

    score: float
    matched_fields: list[str]

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]
