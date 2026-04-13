from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.content import ContentKind
from app.models.learning_path import LearningPath, LearningPathItem
from app.schemas.learning_path import (
    LearningPathContentReferenceCreate,
    LearningPathContentReferenceRead,
    LearningPathCreate,
    LearningPathRead,
    LearningPathUpdate,
)
from app.services.content import resolve_content_reference, serialize_content_summary


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
