from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind, DifficultyLevel, Lab, PublicationStatus
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

router = APIRouter(prefix="/labs", tags=["Labs"])


@router.get("", response_model=list[ContentSummaryRead], summary="List labs")
def list_labs(
    difficulty: DifficultyLevel | None = Query(default=None),
    tags: str | None = Query(default=None, description="Comma-separated tags."),
    status_filter: PublicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[ContentSummaryRead]:
    labs = list_content_items(
        db,
        Lab,
        difficulty=difficulty,
        status_filter=status_filter,
        tags=tags,
    )
    return [serialize_content_summary(lab) for lab in labs]


@router.get("/slug/{lab_slug}", response_model=ContentDetailRead, summary="Get a lab by slug")
def get_lab_by_slug(
    lab_slug: str,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    return serialize_content_detail(get_content_item_by_slug_or_404(db, Lab, lab_slug))


@router.get("/{lab_id}", response_model=ContentDetailRead, summary="Get a lab")
def get_lab(lab_id: int, db: Session = Depends(get_db)) -> ContentDetailRead:
    return serialize_content_detail(get_content_item_or_404(db, Lab, lab_id))


@router.post(
    "",
    response_model=ContentDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lab",
)
def create_lab(payload: ContentCreate, db: Session = Depends(get_db)) -> ContentDetailRead:
    return serialize_content_detail(create_content_item(db, Lab, payload, ContentKind.lab))


@router.put("/{lab_id}", response_model=ContentDetailRead, summary="Update a lab")
def update_lab(
    lab_id: int,
    payload: ContentUpdate,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    lab = get_content_item_or_404(db, Lab, lab_id)
    return serialize_content_detail(update_content_item(db, lab, payload))


@router.delete(
    "/{lab_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lab",
)
def delete_lab(lab_id: int, db: Session = Depends(get_db)) -> Response:
    lab = get_content_item_or_404(db, Lab, lab_id)
    delete_content_item(db, lab)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
