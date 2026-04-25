from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.api._conditional import compute_etag, not_modified
from app.api.dependencies import get_db
from app.models.content import ContentKind
from app.schemas.search import SearchResponse
from app.services.search import search_content

router = APIRouter(prefix="/search", tags=["Search"])

SEARCH_CACHE_CONTROL = "public, max-age=60"


@router.get(
    "",
    response_model=SearchResponse,
    summary="Weighted keyword search across published content",
    description=(
        "Ranks published courses, tutorials, and labs by weighted matches over "
        "title, tags, description, and author. `body_markdown` is not searched. "
        "Public, no auth required. `total` counts all matches across pages; "
        "`has_more` is true when more results exist beyond `offset + limit`. "
        "Supports `If-None-Match` against the response `ETag`; returns 304 when fresh."
    ),
)
def get_search(
    request: Request,
    response: Response,
    q: str = Query(..., min_length=2, max_length=200, description="Search query."),
    content_type: ContentKind | None = Query(
        default=None,
        description="Optional filter to a single content type.",
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum results per page."),
    offset: int = Query(default=0, ge=0, description="Zero-based index of the first result to return."),
    db: Session = Depends(get_db),
) -> Response:
    results, total = search_content(
        db,
        query=q,
        content_type=content_type,
        limit=limit,
        offset=offset,
    )
    payload = SearchResponse(
        query=q,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(results)) < total,
        results=results,
    )

    etag = compute_etag(payload.model_dump(mode="json"))

    if not_modified(request, etag):
        return Response(
            status_code=304,
            headers={"ETag": etag, "Cache-Control": SEARCH_CACHE_CONTROL},
        )

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = SEARCH_CACHE_CONTROL
    return payload
