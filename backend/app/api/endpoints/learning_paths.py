from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.learning_path import (
    LearningPathCreate,
    LearningPathRead,
    LearningPathUpdate,
)
from app.services.learning_paths import (
    create_learning_path,
    delete_learning_path,
    get_learning_path_by_slug_or_404,
    get_learning_path_or_404,
    list_learning_paths,
    serialize_learning_path,
    update_learning_path,
)

router = APIRouter(prefix="/learning-paths", tags=["Learning Paths"])


@router.get("", response_model=list[LearningPathRead], summary="List learning paths")
def get_learning_paths(db: Session = Depends(get_db)) -> list[LearningPathRead]:
    return list_learning_paths(db)


@router.get(
    "/slug/{learning_path_slug}",
    response_model=LearningPathRead,
    summary="Get a learning path by slug",
)
def get_learning_path_by_slug(
    learning_path_slug: str,
    db: Session = Depends(get_db),
) -> LearningPathRead:
    return serialize_learning_path(db, get_learning_path_by_slug_or_404(db, learning_path_slug))


@router.get(
    "/{learning_path_id}",
    response_model=LearningPathRead,
    summary="Get a learning path",
)
def get_learning_path(
    learning_path_id: int,
    db: Session = Depends(get_db),
) -> LearningPathRead:
    return serialize_learning_path(db, get_learning_path_or_404(db, learning_path_id))


@router.post(
    "",
    response_model=LearningPathRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a learning path",
)
def create_learning_path_endpoint(
    payload: LearningPathCreate,
    db: Session = Depends(get_db),
) -> LearningPathRead:
    return create_learning_path(db, payload)


@router.put(
    "/{learning_path_id}",
    response_model=LearningPathRead,
    summary="Update a learning path",
)
def update_learning_path_endpoint(
    learning_path_id: int,
    payload: LearningPathUpdate,
    db: Session = Depends(get_db),
) -> LearningPathRead:
    learning_path = get_learning_path_or_404(db, learning_path_id)
    return update_learning_path(db, learning_path, payload)


@router.delete(
    "/{learning_path_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a learning path",
)
def delete_learning_path_endpoint(
    learning_path_id: int,
    db: Session = Depends(get_db),
) -> Response:
    learning_path = get_learning_path_or_404(db, learning_path_id)
    delete_learning_path(db, learning_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
