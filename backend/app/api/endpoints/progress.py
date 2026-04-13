from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models import User
from app.models.content import ContentKind
from app.schemas.content import ContentSummaryRead
from app.schemas.progress import ProgressListItem, ProgressRead, ProgressUpsert
from app.services.progress import (
    ContentNotFoundError,
    get_progress,
    list_all_progress,
    list_in_progress,
    upsert_progress,
)

router = APIRouter(prefix="/me", tags=["Progress"])


@router.put("/progress", response_model=ProgressRead | None)
def put_progress(
    payload: ProgressUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressRead | None:
    try:
        record = upsert_progress(
            db,
            current_user,
            payload.content_type.value,
            payload.content_id,
            payload.status,
        )
    except ContentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None

    if record is None:
        return None
    return ProgressRead.model_validate(record)


@router.get("/progress", response_model=ProgressRead | None)
def read_progress(
    content_type: ContentKind = Query(..., description="Content type to look up"),
    content_id: int = Query(..., ge=1, description="Content row id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressRead | None:
    record = get_progress(db, current_user, content_type.value, content_id)
    if record is None:
        return None
    return ProgressRead.model_validate(record)


@router.get("/progress/index", response_model=list[ProgressRead])
def index_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProgressRead]:
    return [ProgressRead.model_validate(row) for row in list_all_progress(db, current_user)]


@router.get("/progress/list", response_model=list[ProgressListItem])
def list_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProgressListItem]:
    pairs = list_in_progress(db, current_user)
    return [
        ProgressListItem(
            content_type=row.content_type,
            content_id=row.content_id,
            status=row.status,
            updated_at=row.updated_at,
            content=ContentSummaryRead.model_validate(content),
        )
        for row, content in pairs
    ]
