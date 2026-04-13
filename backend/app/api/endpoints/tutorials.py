from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind, DifficultyLevel, PublicationStatus, Tutorial
from app.schemas.content import (
    ContentCreate,
    ContentDetailRead,
    ContentSummaryRead,
    ContentUpdate,
)
from app.services.content import (
    create_content_item,
    delete_content_item,
    get_content_item_by_slug_or_404,
    get_content_item_or_404,
    list_content_items,
    serialize_content_detail,
    serialize_content_summary,
    update_content_item,
)

router = APIRouter(prefix="/tutorials", tags=["Tutorials"])


@router.get("", response_model=list[ContentSummaryRead], summary="List tutorials")
def list_tutorials(
    difficulty: DifficultyLevel | None = Query(default=None),
    tags: str | None = Query(default=None, description="Comma-separated tags."),
    status_filter: PublicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[ContentSummaryRead]:
    tutorials = list_content_items(
        db,
        Tutorial,
        difficulty=difficulty,
        status_filter=status_filter,
        tags=tags,
    )
    return [serialize_content_summary(tutorial) for tutorial in tutorials]


@router.get(
    "/slug/{tutorial_slug}",
    response_model=ContentDetailRead,
    summary="Get a tutorial by slug",
)
def get_tutorial_by_slug(
    tutorial_slug: str,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    return serialize_content_detail(
        get_content_item_by_slug_or_404(db, Tutorial, tutorial_slug)
    )


@router.get("/{tutorial_id}", response_model=ContentDetailRead, summary="Get a tutorial")
def get_tutorial(tutorial_id: int, db: Session = Depends(get_db)) -> ContentDetailRead:
    return serialize_content_detail(get_content_item_or_404(db, Tutorial, tutorial_id))


@router.post(
    "",
    response_model=ContentDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tutorial",
)
def create_tutorial(
    payload: ContentCreate,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    return serialize_content_detail(
        create_content_item(db, Tutorial, payload, ContentKind.tutorial)
    )


@router.put(
    "/{tutorial_id}",
    response_model=ContentDetailRead,
    summary="Update a tutorial",
)
def update_tutorial(
    tutorial_id: int,
    payload: ContentUpdate,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    tutorial = get_content_item_or_404(db, Tutorial, tutorial_id)
    return serialize_content_detail(update_content_item(db, tutorial, payload))


@router.delete(
    "/{tutorial_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tutorial",
)
def delete_tutorial(tutorial_id: int, db: Session = Depends(get_db)) -> Response:
    tutorial = get_content_item_or_404(db, Tutorial, tutorial_id)
    delete_content_item(db, tutorial)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
