from datetime import datetime
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.content import (
    ContentKind,
    Course,
    DifficultyLevel,
    Lab,
    PublicationStatus,
    Tutorial,
)
from app.models.learning_path import LearningPathItem
from app.schemas.content import (
    ContentCreate,
    ContentDetailRead,
    ContentSummaryRead,
    ContentUpdate,
)

ContentModel = TypeVar("ContentModel", Course, Tutorial, Lab)

CONTENT_MODEL_MAP: dict[ContentKind, type[Course] | type[Tutorial] | type[Lab]] = {
    ContentKind.course: Course,
    ContentKind.tutorial: Tutorial,
    ContentKind.lab: Lab,
}


def list_content_items(
    db: Session,
    model: type[ContentModel],
    difficulty: DifficultyLevel | None = None,
    status_filter: PublicationStatus | None = None,
    tags: str | None = None,
) -> list[ContentModel]:
    statement = select(model)

    if difficulty is not None:
        statement = statement.where(model.difficulty == difficulty.value)

    if status_filter is not None:
        statement = statement.where(model.status == status_filter.value)

    statement = statement.order_by(model.updated_at.desc(), model.id.desc())
    items = list(db.scalars(statement).all())
    required_tags = normalize_tag_filters(tags)

    if not required_tags:
        return items

    return [item for item in items if has_all_tags(item.tags, required_tags)]


def get_content_item_or_404(
    db: Session,
    model: type[ContentModel],
    item_id: int,
) -> ContentModel:
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} {item_id} was not found.",
        )
    return item


def get_content_item_by_slug_or_404(
    db: Session,
    model: type[ContentModel],
    slug: str,
) -> ContentModel:
    item = db.scalar(select(model).where(model.slug == slug))
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} slug '{slug}' was not found.",
        )
    return item


def create_content_item(
    db: Session,
    model: type[ContentModel],
    payload: ContentCreate,
    content_type: ContentKind,
) -> ContentModel:
    item = model(**payload.model_dump(), content_type=content_type.value)
    db.add(item)
    return persist_content_item(db, item, f"{content_type.value} slug must be unique.")


def update_content_item(
    db: Session,
    item: ContentModel,
    payload: ContentUpdate,
) -> ContentModel:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.add(item)
    return persist_content_item(db, item, "Content slug must be unique.")


def delete_content_item(db: Session, item: ContentModel) -> None:
    ensure_content_not_in_learning_paths(db, item)
    db.delete(item)
    db.commit()


def resolve_content_reference(
    db: Session,
    content_type: ContentKind,
    content_id: int,
) -> Course | Tutorial | Lab:
    model = CONTENT_MODEL_MAP[content_type]
    item = db.get(model, content_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{content_type.value} {content_id} does not exist.",
        )
    return item


def persist_content_item(
    db: Session,
    item: ContentModel,
    duplicate_slug_message: str,
) -> ContentModel:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=duplicate_slug_message,
        ) from exc

    db.refresh(item)
    return item


def serialize_content_summary(item: Course | Tutorial | Lab) -> ContentSummaryRead:
    return ContentSummaryRead.model_validate(item)


def serialize_content_detail(item: Course | Tutorial | Lab) -> ContentDetailRead:
    summary = serialize_content_summary(item)
    return ContentDetailRead(**summary.model_dump(), body_markdown=item.body_markdown)


def list_catalog_items(
    db: Session,
    difficulty: DifficultyLevel | None = None,
    status_filter: PublicationStatus | None = None,
    tags: str | None = None,
    content_type: ContentKind | None = None,
) -> list[ContentSummaryRead]:
    models = (
        [CONTENT_MODEL_MAP[content_type]]
        if content_type is not None
        else [Course, Tutorial, Lab]
    )
    catalog_items: list[Course | Tutorial | Lab] = []

    for model in models:
        catalog_items.extend(
            list_content_items(
                db,
                model,
                difficulty=difficulty,
                status_filter=status_filter,
                tags=tags,
            )
        )

    catalog_items.sort(key=lambda item: (item.updated_at, item.id), reverse=True)
    return [serialize_content_summary(item) for item in catalog_items]


def list_published_feed_items(
    db: Session,
    content_type: ContentKind | None = None,
    updated_since: datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Course | Tutorial | Lab], int]:
    """Return a page of published content for the syndication feed plus the total match count.

    Deterministic ordering: ``updated_at DESC``, then ``slug ASC`` for ties.
    ``updated_since`` is inclusive (>=). ``total`` is the count across all
    pages, not just the returned page.
    """
    models: list[type[Course] | type[Tutorial] | type[Lab]] = (
        [CONTENT_MODEL_MAP[content_type]] if content_type is not None else [Course, Tutorial, Lab]
    )
    results: list[Course | Tutorial | Lab] = []

    for model in models:
        statement = select(model).where(model.status == PublicationStatus.published.value)
        if updated_since is not None:
            statement = statement.where(model.updated_at >= updated_since)
        results.extend(db.scalars(statement).all())

    results.sort(key=lambda item: (-item.updated_at.timestamp(), item.slug))
    total = len(results)
    return results[offset : offset + limit], total


def get_published_feed_item_or_404(
    db: Session,
    content_type: ContentKind,
    slug: str,
) -> Course | Tutorial | Lab:
    """Return one published content item by ``(content_type, slug)`` for syndication.

    Filters on ``status = published`` inside the query. Missing rows and
    unpublished rows both return 404 so drafts are not leaked to external
    consumers.
    """
    model = CONTENT_MODEL_MAP[content_type]
    item = db.scalar(
        select(model).where(
            model.slug == slug,
            model.status == PublicationStatus.published.value,
        )
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published {content_type.value} with slug '{slug}' was not found.",
        )
    return item


def normalize_tag_filters(tags: str | None) -> list[str]:
    if tags is None:
        return []

    return [tag.strip().lower() for tag in tags.split(",") if tag.strip()]


def has_all_tags(item_tags: list[str], required_tags: list[str]) -> bool:
    normalized_item_tags = {tag.lower() for tag in item_tags}
    return all(tag in normalized_item_tags for tag in required_tags)


def ensure_content_not_in_learning_paths(
    db: Session,
    item: Course | Tutorial | Lab,
) -> None:
    reference = db.scalar(
        select(LearningPathItem).where(
            LearningPathItem.content_type == item.content_type,
            LearningPathItem.content_id == item.id,
        )
    )

    if reference is None:
        return

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Content cannot be deleted while it is referenced by a learning path.",
    )
