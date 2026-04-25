"""Weighted keyword search across published content.

DB-agnostic: candidate rows are loaded via SQLAlchemy and scored in Python so
the implementation runs unchanged on Postgres (production) and SQLite (tests).
Intentionally does not use ``tsvector``/GIN or an external index — see the
Phase 4C roadmap entry for the rationale.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import ContentKind, Course, Lab, PublicationStatus, Tutorial
from app.schemas.search import SearchResult
from app.services.content import CONTENT_MODEL_MAP, serialize_content_summary

TITLE_TOKEN_WEIGHT = 10
TAG_TOKEN_WEIGHT = 6
DESCRIPTION_TOKEN_WEIGHT = 3
AUTHOR_TOKEN_WEIGHT = 2

TITLE_PHRASE_BONUS = 8
TAG_PHRASE_BONUS = 4

SEARCHABLE_FIELDS: tuple[str, ...] = ("title", "tags", "description", "author")


@dataclass
class _Scored:
    item: Course | Tutorial | Lab
    score: float
    matched_fields: list[str]


def search_content(
    db: Session,
    query: str,
    content_type: ContentKind | None = None,
    limit: int = 20,
) -> list[SearchResult]:
    """Return ranked search results across published content.

    Weighted matching over title, tags, description, and author. Does not
    search ``body_markdown``. Only items with ``status = published`` are
    considered.
    """
    normalized_query = query.strip().lower()
    tokens = [token for token in normalized_query.split() if token]
    if not tokens:
        return []

    models: list[type[Course] | type[Tutorial] | type[Lab]] = (
        [CONTENT_MODEL_MAP[content_type]] if content_type is not None else [Course, Tutorial, Lab]
    )

    scored: list[_Scored] = []
    for model in models:
        statement = select(model).where(model.status == PublicationStatus.published.value)
        for item in db.scalars(statement).all():
            result = _score_item(item, tokens, normalized_query)
            if result.score > 0:
                scored.append(result)

    scored.sort(key=lambda s: (-s.score, s.item.title.lower(), s.item.slug))

    return [
        SearchResult(
            **serialize_content_summary(s.item).model_dump(),
            score=s.score,
            matched_fields=s.matched_fields,
        )
        for s in scored[:limit]
    ]


def _score_item(
    item: Course | Tutorial | Lab,
    tokens: list[str],
    normalized_query: str,
) -> _Scored:
    title_lower = item.title.lower()
    description_lower = item.description.lower()
    author_lower = item.author.lower()
    tags_joined = " ".join(tag.lower() for tag in item.tags)

    score = 0
    matched: set[str] = set()

    for token in tokens:
        if token in title_lower:
            score += TITLE_TOKEN_WEIGHT
            matched.add("title")
        if token in tags_joined:
            score += TAG_TOKEN_WEIGHT
            matched.add("tags")
        if token in description_lower:
            score += DESCRIPTION_TOKEN_WEIGHT
            matched.add("description")
        if token in author_lower:
            score += AUTHOR_TOKEN_WEIGHT
            matched.add("author")

    if len(tokens) > 1:
        if normalized_query in title_lower:
            score += TITLE_PHRASE_BONUS
        if normalized_query in tags_joined:
            score += TAG_PHRASE_BONUS

    matched_fields = [field for field in SEARCHABLE_FIELDS if field in matched]
    return _Scored(item=item, score=float(score), matched_fields=matched_fields)
