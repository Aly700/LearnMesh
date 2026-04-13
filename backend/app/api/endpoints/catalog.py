from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind, DifficultyLevel, PublicationStatus
from app.schemas.content import ContentSummaryRead
from app.services.content import list_catalog_items

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("", response_model=list[ContentSummaryRead], summary="Browse the full content catalog")
def get_catalog(
    content_type: ContentKind | None = Query(default=None),
    difficulty: DifficultyLevel | None = Query(default=None),
    tags: str | None = Query(default=None, description="Comma-separated tags."),
    status_filter: PublicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[ContentSummaryRead]:
    return list_catalog_items(
        db,
        difficulty=difficulty,
        status_filter=status_filter,
        tags=tags,
        content_type=content_type,
    )
