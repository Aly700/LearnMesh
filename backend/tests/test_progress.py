"""Tests for progress endpoints: upsert, lookup, index, auth gating."""

import pytest
from sqlalchemy.orm import Session

from app.models import Course


@pytest.fixture()
def sample_course(db_session: Session) -> Course:
    """Insert a minimal course for progress tests."""
    course = Course(
        slug="test-course",
        title="Test Course",
        description="A course for testing.",
        body_markdown="# Test",
        difficulty="beginner",
        estimated_minutes=10,
        tags=["test"],
        status="published",
        author="Test Author",
        content_type="course",
    )
    db_session.add(course)
    db_session.flush()
    return course


class TestUpsertProgress:
    def test_set_in_progress(self, client, auth_headers, sample_course):
        resp = client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "in_progress",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_type"] == "course"
        assert data["content_id"] == sample_course.id
        assert data["status"] == "in_progress"

    def test_set_completed(self, client, auth_headers, sample_course):
        # First set in_progress, then completed
        client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "in_progress",
            },
        )
        resp = client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "completed",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_reset_to_not_started_deletes_row(self, client, auth_headers, sample_course):
        # Create a progress row
        client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "in_progress",
            },
        )
        # Reset it
        resp = client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "not_started",
            },
        )
        assert resp.status_code == 200
        assert resp.json() is None

        # Confirm it's gone from the index
        index_resp = client.get("/api/v1/me/progress/index", headers=auth_headers)
        assert index_resp.status_code == 200
        assert len(index_resp.json()) == 0

    def test_nonexistent_content_returns_404(self, client, auth_headers):
        resp = client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": 99999,
                "status": "in_progress",
            },
        )
        assert resp.status_code == 404


class TestGetProgress:
    def test_lookup_existing(self, client, auth_headers, sample_course):
        client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "completed",
            },
        )
        resp = client.get(
            "/api/v1/me/progress",
            headers=auth_headers,
            params={"content_type": "course", "content_id": sample_course.id},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_lookup_no_progress_returns_null(self, client, auth_headers, sample_course):
        resp = client.get(
            "/api/v1/me/progress",
            headers=auth_headers,
            params={"content_type": "course", "content_id": sample_course.id},
        )
        assert resp.status_code == 200
        assert resp.json() is None


class TestProgressIndex:
    def test_index_returns_all_statuses(self, client, auth_headers, sample_course):
        client.put(
            "/api/v1/me/progress",
            headers=auth_headers,
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "completed",
            },
        )
        resp = client.get("/api/v1/me/progress/index", headers=auth_headers)
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 1
        assert rows[0]["content_type"] == "course"
        assert rows[0]["status"] == "completed"


class TestProgressAuthGating:
    def test_upsert_requires_auth(self, client, sample_course):
        resp = client.put(
            "/api/v1/me/progress",
            json={
                "content_type": "course",
                "content_id": sample_course.id,
                "status": "in_progress",
            },
        )
        assert resp.status_code == 401

    def test_index_requires_auth(self, client):
        resp = client.get("/api/v1/me/progress/index")
        assert resp.status_code == 401

    def test_lookup_requires_auth(self, client, sample_course):
        resp = client.get(
            "/api/v1/me/progress",
            params={"content_type": "course", "content_id": sample_course.id},
        )
        assert resp.status_code == 401
