from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.content import ContentKind, Course, DifficultyLevel, PublicationStatus
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

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[ContentSummaryRead], summary="List courses")
def list_courses(
    difficulty: DifficultyLevel | None = Query(default=None),
    tags: str | None = Query(default=None, description="Comma-separated tags."),
    status_filter: PublicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[ContentSummaryRead]:
    courses = list_content_items(
        db,
        Course,
        difficulty=difficulty,
        status_filter=status_filter,
        tags=tags,
    )
    return [serialize_content_summary(course) for course in courses]


@router.get(
    "/slug/{course_slug}",
    response_model=ContentDetailRead,
    summary="Get a course by slug",
)
def get_course_by_slug(
    course_slug: str,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    return serialize_content_detail(get_content_item_by_slug_or_404(db, Course, course_slug))


@router.get("/{course_id}", response_model=ContentDetailRead, summary="Get a course")
def get_course(course_id: int, db: Session = Depends(get_db)) -> ContentDetailRead:
    return serialize_content_detail(get_content_item_or_404(db, Course, course_id))


@router.post(
    "",
    response_model=ContentDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course",
)
def create_course(payload: ContentCreate, db: Session = Depends(get_db)) -> ContentDetailRead:
    return serialize_content_detail(
        create_content_item(db, Course, payload, ContentKind.course)
    )


@router.put("/{course_id}", response_model=ContentDetailRead, summary="Update a course")
def update_course(
    course_id: int,
    payload: ContentUpdate,
    db: Session = Depends(get_db),
) -> ContentDetailRead:
    course = get_content_item_or_404(db, Course, course_id)
    return serialize_content_detail(update_content_item(db, course, payload))


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course",
)
def delete_course(course_id: int, db: Session = Depends(get_db)) -> Response:
    course = get_content_item_or_404(db, Course, course_id)
    delete_content_item(db, course)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
