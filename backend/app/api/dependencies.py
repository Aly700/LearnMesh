from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User
from app.services.auth import AuthError, decode_access_token, get_user_by_id


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Not authenticated")
    try:
        subject = decode_access_token(credentials.credentials)
    except AuthError:
        raise _unauthorized("Invalid authentication credentials") from None
    try:
        user_id = int(subject)
    except ValueError:
        raise _unauthorized("Invalid authentication credentials") from None
    user = get_user_by_id(db, user_id)
    if user is None:
        raise _unauthorized("User not found")
    return user
