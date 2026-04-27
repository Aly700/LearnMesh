from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.content import ContentKind, Course, Lab, PublicationStatus, Tutorial
from app.models.learning_path import LearningPath, LearningPathItem
from app.schemas.learning_path import (
    LearningPathContentReferenceCreate,
    LearningPathContentReferenceRead,
    LearningPathCreate,
    LearningPathRead,
    LearningPathUpdate,
)
from app.schemas.syndication import (
    LearningPathFeedDetail,
    LearningPathFeedStep,
    LearningPathFeedSummary,
)
from app.services.content import (
    CONTENT_MODEL_MAP,
    resolve_content_reference,
    serialize_content_summary,
)


def list_learning_paths(db: Session) -> list[LearningPathRead]:
    statement = (
        select(LearningPath)
        .options(selectinload(LearningPath.items))
        .order_by(LearningPath.updated_at.desc(), LearningPath.id.desc())
    )
    learning_paths = list(db.scalars(statement).all())
    return [serialize_learning_path(db, learning_path) for learning_path in learning_paths]


def get_learning_path_or_404(db: Session, learning_path_id: int) -> LearningPath:
    statement = (
        select(LearningPath)
        .options(selectinload(LearningPath.items))
        .where(LearningPath.id == learning_path_id)
    )
    learning_path = db.scalar(statement)
    if learning_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning path {learning_path_id} was not found.",
        )
    return learning_path


def get_learning_path_by_slug_or_404(db: Session, slug: str) -> LearningPath:
    statement = (
        select(LearningPath)
        .options(selectinload(LearningPath.items))
        .where(LearningPath.slug == slug)
    )
    learning_path = db.scalar(statement)
    if learning_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning path slug '{slug}' was not found.",
        )
    return learning_path


def create_learning_path(db: Session, payload: LearningPathCreate) -> LearningPathRead:
    learning_path = LearningPath(
        slug=payload.slug,
        title=payload.title,
        description=payload.description,
    )
    db.add(learning_path)
    db.flush()
    sync_learning_path_items(db, learning_path, payload.ordered_content)
    commit_learning_path(db, "Learning path slug must be unique.")
    return serialize_learning_path(db, get_learning_path_or_404(db, learning_path.id))


def update_learning_path(
    db: Session,
    learning_path: LearningPath,
    payload: LearningPathUpdate,
) -> LearningPathRead:
    update_data = payload.model_dump(exclude_unset=True, exclude={"ordered_content"})

    for field, value in update_data.items():
        setattr(learning_path, field, value)

    if payload.ordered_content is not None:
        sync_learning_path_items(db, learning_path, payload.ordered_content)
        learning_path.updated_at = func.now()

    db.add(learning_path)
    commit_learning_path(db, "Learning path slug must be unique.")
    return serialize_learning_path(db, get_learning_path_or_404(db, learning_path.id))


def delete_learning_path(db: Session, learning_path: LearningPath) -> None:
    db.delete(learning_path)
    db.commit()


def sync_learning_path_items(
    db: Session,
    learning_path: LearningPath,
    ordered_content: list[LearningPathContentReferenceCreate],
) -> None:
    normalized_items: list[LearningPathItem] = []

    for default_position, reference in enumerate(ordered_content, start=1):
        content_item = resolve_content_reference(
            db,
            reference.content_type,
            reference.content_id,
        )
        normalized_items.append(
            LearningPathItem(
                position=reference.position or default_position,
                content_type=content_item.content_type,
                content_id=content_item.id,
                content_slug=content_item.slug,
                content_title=content_item.title,
            )
        )

    normalized_items.sort(key=lambda item: item.position)
    learning_path.items.clear()
    db.flush()

    for position, item in enumerate(normalized_items, start=1):
        item.position = position
        learning_path.items.append(item)


def commit_learning_path(db: Session, duplicate_slug_message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=duplicate_slug_message,
        ) from exc


def serialize_learning_path(
    db: Session,
    learning_path: LearningPath,
) -> LearningPathRead:
    ordered_content = [
        serialize_learning_path_step(db, reference)
        for reference in learning_path.items
    ]

    return LearningPathRead(
        id=learning_path.id,
        slug=learning_path.slug,
        title=learning_path.title,
        description=learning_path.description,
        step_count=len(ordered_content),
        estimated_minutes_total=sum(
            item.estimated_minutes for item in ordered_content
        ),
        created_at=learning_path.created_at,
        updated_at=learning_path.updated_at,
        ordered_content=ordered_content,
    )


def _publishable_pairs(
    db: Session,
    learning_path: LearningPath,
) -> list[tuple[LearningPathItem, Course | Tutorial | Lab]]:
    """Return the ordered ``(item, content_row)`` pairs for a path's published steps.

    Filters out steps whose ``content_type`` is unknown, whose content row is
    missing (orphaned), or whose content row is not ``status = published``.
    Original ``position`` order is preserved (gaps intentional). Returns ``[]``
    when no step survives filtering.
    """
    pairs: list[tuple[LearningPathItem, Course | Tutorial | Lab]] = []
    for item in learning_path.items:
        try:
            kind = ContentKind(item.content_type)
        except ValueError:
            continue
        model = CONTENT_MODEL_MAP[kind]
        content_row = db.get(model, item.content_id)
        if content_row is None:
            continue
        if content_row.status != PublicationStatus.published.value:
            continue
        pairs.append((item, content_row))
    return pairs


def get_published_learning_path_or_404(
    db: Session,
    slug: str,
) -> tuple[LearningPath, list[tuple[LearningPathItem, Course | Tutorial | Lab]]]:
    """Return a learning path by slug along with its published step pairs.

    A learning path is "published" iff at least one of its ordered steps
    resolves to a content row with ``status = published``. Unpublished and
    orphaned (missing) steps are filtered out. Returns ``(path, pairs)`` where
    ``pairs`` is ``[(item, content_row), ...]`` in original ``position`` order
    (gaps preserved). Raises 404 if the path does not exist or no steps
    survive filtering.
    """
    statement = (
        select(LearningPath)
        .options(selectinload(LearningPath.items))
        .where(LearningPath.slug == slug)
    )
    learning_path = db.scalar(statement)
    if learning_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published learning path with slug '{slug}' was not found.",
        )

    pairs = _publishable_pairs(db, learning_path)
    if not pairs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published learning path with slug '{slug}' was not found.",
        )

    return learning_path, pairs


def list_publishable_learning_paths(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[LearningPathFeedSummary], int]:
    """Return a page of publishable learning-path summaries plus the total match count.

    A path is included iff it has at least one step that resolves to a
    ``status = published`` content row (same gate as Phase 4F). Deterministic
    ordering: ``updated_at DESC``, tie-break on ``slug ASC``. ``total`` counts
    all publishable paths across pages.
    """
    statement = (
        select(LearningPath)
        .options(selectinload(LearningPath.items))
        .order_by(LearningPath.updated_at.desc(), LearningPath.slug.asc())
    )
    publishable: list[LearningPathFeedSummary] = []
    for path in db.scalars(statement).all():
        pairs = _publishable_pairs(db, path)
        if not pairs:
            continue
        publishable.append(serialize_publishable_learning_path_summary(path, pairs))

    total = len(publishable)
    return publishable[offset : offset + limit], total


def serialize_publishable_learning_path_summary(
    learning_path: LearningPath,
    published_pairs: list[tuple[LearningPathItem, Course | Tutorial | Lab]],
) -> LearningPathFeedSummary:
    """Build the slim feed summary for a publishable learning path."""
    return LearningPathFeedSummary(
        slug=learning_path.slug,
        title=learning_path.title,
        description=learning_path.description,
        step_count=len(published_pairs),
        estimated_minutes_total=sum(content_row.estimated_minutes for _, content_row in published_pairs),
        created_at=learning_path.created_at,
        updated_at=learning_path.updated_at,
    )


def serialize_published_learning_path(
    learning_path: LearningPath,
    published_pairs: list[tuple[LearningPathItem, Course | Tutorial | Lab]],
) -> LearningPathFeedDetail:
    """Build the public syndication payload for a published learning path."""
    steps = [
        LearningPathFeedStep(
            position=item.position,
            content_type=ContentKind(content_row.content_type),
            slug=content_row.slug,
            title=content_row.title,
        )
        for item, content_row in published_pairs
    ]
    return LearningPathFeedDetail(
        slug=learning_path.slug,
        title=learning_path.title,
        description=learning_path.description,
        step_count=len(steps),
        estimated_minutes_total=sum(content_row.estimated_minutes for _, content_row in published_pairs),
        created_at=learning_path.created_at,
        updated_at=learning_path.updated_at,
        steps=steps,
    )


def published_learning_path_last_modified(
    learning_path: LearningPath,
    published_pairs: list[tuple[LearningPathItem, Course | Tutorial | Lab]],
) -> datetime:
    """Return ``MAX(path.updated_at, max(member.updated_at))`` over published members."""
    return max(
        learning_path.updated_at,
        *(content_row.updated_at for _, content_row in published_pairs),
    )


def serialize_learning_path_step(
    db: Session,
    reference: LearningPathItem,
) -> LearningPathContentReferenceRead:
    content_item = resolve_content_reference(
        db,
        ContentKind(reference.content_type),
        reference.content_id,
    )
    summary = serialize_content_summary(content_item)

    return LearningPathContentReferenceRead(
        id=reference.id,
        content_type=summary.content_type,
        content_id=summary.id,
        position=reference.position,
        content_slug=summary.slug,
        content_title=summary.title,
        description=summary.description,
        difficulty=summary.difficulty,
        estimated_minutes=summary.estimated_minutes,
        tags=summary.tags,
        status=summary.status,
        author=summary.author,
    )
