from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind
from app.schemas.search import SearchResponse
from app.services.search import search_content

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=SearchResponse,
    summary="Weighted keyword search across published content",
    description=(
        "Ranks published courses, tutorials, and labs by weighted matches over "
        "title, tags, description, and author. `body_markdown` is not searched. "
        "Public, no auth required."
    ),
)
def get_search(
    q: str = Query(..., min_length=2, max_length=200, description="Search query."),
    content_type: ContentKind | None = Query(
        default=None,
        description="Optional filter to a single content type.",
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum results to return."),
    db: Session = Depends(get_db),
) -> SearchResponse:
    results = search_content(db, query=q, content_type=content_type, limit=limit)
    return SearchResponse(query=q, total=len(results), results=results)
