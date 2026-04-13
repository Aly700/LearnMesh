"""Test infrastructure for LearnMesh backend.

Provides a fully isolated SQLite in-memory database, a FastAPI TestClient,
and auth helper fixtures. No connection to the real Postgres database.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app

# ---------------------------------------------------------------------------
# SQLite in-memory engine — shared across all tests in a session
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable SQLite foreign key enforcement (off by default)
@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, class_=Session,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    """Create all tables once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional test session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    # Override the FastAPI dependency for the duration of this test
    app.dependency_overrides[get_db] = lambda: session

    yield session

    session.close()
    transaction.rollback()
    connection.close()

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Starlette test client bound to the FastAPI app (no real server started)."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

_test_user_counter = 0


def _unique_email() -> str:
    global _test_user_counter
    _test_user_counter += 1
    return f"test{_test_user_counter}@example.com"


@pytest.fixture()
def registered_user(client: TestClient) -> dict:
    """Register a fresh user and return {"email", "password", "token", "user"}."""
    email = _unique_email()
    password = "testpass123"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 201
    data = resp.json()
    return {
        "email": email,
        "password": password,
        "token": data["access_token"],
        "user": data["user"],
    }


@pytest.fixture()
def auth_headers(registered_user: dict) -> dict[str, str]:
    """Authorization headers for the registered test user."""
    return {"Authorization": f"Bearer {registered_user['token']}"}
