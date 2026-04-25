from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind
from app.schemas.syndication import FeedItem, FeedItemDetail, FeedMeta, FeedResponse
from app.services.content import get_published_feed_item_or_404, list_published_feed_items

router = APIRouter(prefix="/syndication", tags=["Syndication"])


@router.get(
    "/feed",
    response_model=FeedResponse,
    summary="Public content syndication feed",
    description=(
        "Returns a page of published content (courses, tutorials, labs) for external "
        "consumption. Use `content_type` + `slug` as the stable external identifier "
        "for each item. `meta.total` counts all matching items across pages; "
        "`meta.has_more` is true when more items exist beyond `offset + limit`."
    ),
)
def get_feed(
    response: Response,
    content_type: ContentKind | None = Query(default=None, description="Filter to a single content type."),
    updated_since: datetime | None = Query(
        default=None,
        description="ISO 8601 timestamp. Only items updated at or after this time are returned (inclusive).",
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum items per page."),
    offset: int = Query(default=0, ge=0, description="Zero-based index of the first item to return."),
    db: Session = Depends(get_db),
) -> FeedResponse:
    items, total = list_published_feed_items(
        db,
        content_type=content_type,
        updated_since=updated_since,
        limit=limit,
        offset=offset,
    )
    feed_items = [FeedItem.model_validate(item) for item in items]
    response.headers["Cache-Control"] = "public, max-age=60"
    return FeedResponse(
        meta=FeedMeta(
            total=total,
            generated_at=datetime.now(UTC),
            limit=limit,
            offset=offset,
            has_more=(offset + len(feed_items)) < total,
        ),
        items=feed_items,
    )


@router.get(
    "/content/{content_type}/{slug}",
    response_model=FeedItemDetail,
    summary="Public single-item syndication detail",
    description=(
        "Returns one published content item (course, tutorial, or lab) addressed by the "
        "stable external identifier `content_type` + `slug`. Unpublished or missing items "
        "return 404 so drafts are not exposed."
    ),
)
def get_content_detail(
    response: Response,
    content_type: ContentKind,
    slug: str,
    db: Session = Depends(get_db),
) -> FeedItemDetail:
    item = get_published_feed_item_or_404(db, content_type, slug)
    response.headers["Cache-Control"] = "public, max-age=300"
    return FeedItemDetail.model_validate(item)
