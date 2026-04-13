from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ContentProgress, Course, Lab, Tutorial, User
from app.models.content import ContentKind
from app.schemas.progress import ProgressStatus

_CONTENT_MODELS: dict[str, type[Course] | type[Tutorial] | type[Lab]] = {
    ContentKind.course.value: Course,
    ContentKind.tutorial.value: Tutorial,
    ContentKind.lab.value: Lab,
}


class ContentNotFoundError(Exception):
    """Raised when a (content_type, content_id) pair does not match any row."""


def _content_exists(session: Session, content_type: str, content_id: int) -> bool:
    model = _CONTENT_MODELS.get(content_type)
    if model is None:
        return False
    return session.get(model, content_id) is not None


def get_progress(
    session: Session,
    user: User,
    content_type: str,
    content_id: int,
) -> ContentProgress | None:
    return session.scalar(
        select(ContentProgress).where(
            ContentProgress.user_id == user.id,
            ContentProgress.content_type == content_type,
            ContentProgress.content_id == content_id,
        )
    )


def upsert_progress(
    session: Session,
    user: User,
    content_type: str,
    content_id: int,
    status: ProgressStatus,
) -> ContentProgress | None:
    if not _content_exists(session, content_type, content_id):
        raise ContentNotFoundError(
            f"{content_type} with id {content_id} does not exist"
        )

    existing = get_progress(session, user, content_type, content_id)

    if status == ProgressStatus.not_started:
        if existing is not None:
            session.delete(existing)
            session.commit()
        return None

    if existing is None:
        record = ContentProgress(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id,
            status=status.value,
        )
        session.add(record)
    else:
        existing.status = status.value
        record = existing

    session.commit()
    session.refresh(record)
    return record


def list_all_progress(session: Session, user: User) -> list[ContentProgress]:
    return list(
        session.scalars(
            select(ContentProgress)
            .where(ContentProgress.user_id == user.id)
            .order_by(ContentProgress.updated_at.desc())
        )
    )


def list_in_progress(session: Session, user: User) -> list[tuple[ContentProgress, object]]:
    rows = list(
        session.scalars(
            select(ContentProgress)
            .where(
                ContentProgress.user_id == user.id,
                ContentProgress.status == ProgressStatus.in_progress.value,
            )
            .order_by(ContentProgress.updated_at.desc())
        )
    )
    if not rows:
        return []

    ids_by_type: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        ids_by_type[row.content_type].append(row.content_id)

    content_by_key: dict[tuple[str, int], object] = {}
    for content_type, ids in ids_by_type.items():
        model = _CONTENT_MODELS.get(content_type)
        if model is None:
            continue
        records = session.scalars(select(model).where(model.id.in_(ids))).all()
        for record in records:
            content_by_key[(content_type, record.id)] = record

    paired: list[tuple[ContentProgress, object]] = []
    for row in rows:
        content = content_by_key.get((row.content_type, row.content_id))
        if content is None:
            continue
        paired.append((row, content))
    return paired
