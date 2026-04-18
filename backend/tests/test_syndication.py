"""Tests for the content syndication feed endpoint."""

import pytest
from sqlalchemy.orm import Session

from app.models.content import Course, Lab, Tutorial

FEED_URL = "/api/v1/syndication/feed"


@pytest.fixture()
def published_course(db_session: Session) -> Course:
    course = Course(
        slug="syndication-course",
        title="Syndication Course",
        description="A published course for syndication tests.",
        body_markdown="# Content",
        difficulty="beginner",
        estimated_minutes=30,
        tags=["python", "testing"],
        status="published",
        author="Test Author",
        content_type="course",
    )
    db_session.add(course)
    db_session.flush()
    return course


@pytest.fixture()
def published_tutorial(db_session: Session) -> Tutorial:
    tutorial = Tutorial(
        slug="syndication-tutorial",
        title="Syndication Tutorial",
        description="A published tutorial for syndication tests.",
        body_markdown="# Tutorial",
        difficulty="intermediate",
        estimated_minutes=15,
        tags=["docker"],
        status="published",
        author="Test Author",
        content_type="tutorial",
    )
    db_session.add(tutorial)
    db_session.flush()
    return tutorial


@pytest.fixture()
def draft_lab(db_session: Session) -> Lab:
    lab = Lab(
        slug="draft-lab",
        title="Draft Lab",
        description="A draft lab that should NOT appear in the feed.",
        body_markdown="# Draft",
        difficulty="advanced",
        estimated_minutes=60,
        tags=["kubernetes"],
        status="draft",
        author="Test Author",
        content_type="lab",
    )
    db_session.add(lab)
    db_session.flush()
    return lab


class TestFeedBasics:
    def test_empty_feed(self, client):
        resp = client.get(FEED_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["total"] == 0
        assert data["items"] == []
        assert "generated_at" in data["meta"]

    def test_feed_returns_published_content(self, client, published_course, published_tutorial):
        resp = client.get(FEED_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["total"] == 2
        slugs = {item["slug"] for item in data["items"]}
        assert slugs == {"syndication-course", "syndication-tutorial"}

    def test_feed_excludes_drafts(self, client, published_course, draft_lab):
        resp = client.get(FEED_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["total"] == 1
        assert data["items"][0]["slug"] == "syndication-course"

    def test_feed_item_shape(self, client, published_course):
        resp = client.get(FEED_URL)
        item = resp.json()["items"][0]
        assert item["content_type"] == "course"
        assert item["slug"] == "syndication-course"
        assert item["title"] == "Syndication Course"
        assert item["difficulty"] == "beginner"
        assert item["estimated_minutes"] == 30
        assert item["tags"] == ["python", "testing"]
        assert item["author"] == "Test Author"
        assert "created_at" in item
        assert "updated_at" in item
        # Must NOT include internal fields
        assert "id" not in item
        assert "body_markdown" not in item
        assert "status" not in item

    def test_no_auth_required(self, client, published_course):
        resp = client.get(FEED_URL)
        assert resp.status_code == 200


class TestFeedFiltering:
    def test_filter_by_content_type(self, client, published_course, published_tutorial):
        resp = client.get(FEED_URL, params={"content_type": "course"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["total"] == 1
        assert data["items"][0]["content_type"] == "course"

    def test_filter_invalid_content_type(self, client):
        resp = client.get(FEED_URL, params={"content_type": "podcast"})
        assert resp.status_code == 422


class TestUpdatedSince:
    def test_updated_since_far_future(self, client, published_course):
        resp = client.get(FEED_URL, params={"updated_since": "2099-01-01T00:00:00Z"})
        assert resp.status_code == 200
        assert resp.json()["meta"]["total"] == 0

    def test_updated_since_far_past(self, client, published_course):
        resp = client.get(FEED_URL, params={"updated_since": "2000-01-01T00:00:00Z"})
        assert resp.status_code == 200
        assert resp.json()["meta"]["total"] == 1

    def test_updated_since_invalid_format(self, client):
        resp = client.get(FEED_URL, params={"updated_since": "not-a-date"})
        assert resp.status_code == 422
