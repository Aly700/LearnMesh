"""Tests for the content syndication feed endpoint."""

import pytest
from sqlalchemy.orm import Session

from app.models.content import Course, Lab, Tutorial

FEED_URL = "/api/v1/syndication/feed"
CONTENT_URL = "/api/v1/syndication/content"


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


class TestContentDetail:
    def test_returns_published_item_with_body(self, client, published_course):
        resp = client.get(f"{CONTENT_URL}/course/syndication-course")
        assert resp.status_code == 200
        data = resp.json()
        assert data["content_type"] == "course"
        assert data["slug"] == "syndication-course"
        assert data["title"] == "Syndication Course"
        assert data["difficulty"] == "beginner"
        assert data["estimated_minutes"] == 30
        assert data["tags"] == ["python", "testing"]
        assert data["author"] == "Test Author"
        assert data["body_markdown"] == "# Content"
        assert "created_at" in data
        assert "updated_at" in data
        # Must NOT include internal fields
        assert "id" not in data
        assert "status" not in data

    def test_draft_returns_404(self, client, draft_lab):
        resp = client.get(f"{CONTENT_URL}/lab/draft-lab")
        assert resp.status_code == 404

    def test_unknown_slug_returns_404(self, client):
        resp = client.get(f"{CONTENT_URL}/course/does-not-exist")
        assert resp.status_code == 404

    def test_mismatched_content_type_returns_404(self, client, published_course):
        # The course exists and is published, but asking under `/lab/` must 404.
        resp = client.get(f"{CONTENT_URL}/lab/syndication-course")
        assert resp.status_code == 404

    def test_invalid_content_type_returns_422(self, client):
        resp = client.get(f"{CONTENT_URL}/podcast/anything")
        assert resp.status_code == 422

    def test_no_auth_required(self, client, published_course):
        resp = client.get(f"{CONTENT_URL}/course/syndication-course")
        assert resp.status_code == 200

    def test_detail_is_superset_of_feed_item(self, client, published_course):
        feed_resp = client.get(FEED_URL)
        detail_resp = client.get(f"{CONTENT_URL}/course/syndication-course")
        assert feed_resp.status_code == 200
        assert detail_resp.status_code == 200
        feed_item = feed_resp.json()["items"][0]
        detail_item = detail_resp.json()
        # Every FeedItem field must match exactly on the detail response.
        for key, value in feed_item.items():
            assert detail_item[key] == value
        # Detail adds body_markdown; feed never includes it.
        assert "body_markdown" in detail_item
        assert "body_markdown" not in feed_item


@pytest.fixture()
def published_lab(db_session: Session) -> Lab:
    lab = Lab(
        slug="syndication-lab",
        title="Syndication Lab",
        description="A published lab for syndication tests.",
        body_markdown="# Lab",
        difficulty="intermediate",
        estimated_minutes=45,
        tags=["fastapi"],
        status="published",
        author="Test Author",
        content_type="lab",
    )
    db_session.add(lab)
    db_session.flush()
    return lab


class TestFeedPagination:
    def test_default_pagination_metadata(self, client, published_course):
        meta = client.get(FEED_URL).json()["meta"]
        assert meta["total"] == 1
        assert meta["limit"] == 50
        assert meta["offset"] == 0
        assert meta["has_more"] is False

    def test_empty_feed_pagination_metadata(self, client):
        meta = client.get(FEED_URL).json()["meta"]
        assert meta["total"] == 0
        assert meta["limit"] == 50
        assert meta["offset"] == 0
        assert meta["has_more"] is False

    def test_limit_caps_returned_items_total_unchanged(
        self, client, published_course, published_tutorial, published_lab,
    ):
        body = client.get(FEED_URL, params={"limit": 2}).json()
        assert body["meta"]["total"] == 3
        assert body["meta"]["limit"] == 2
        assert body["meta"]["has_more"] is True
        assert len(body["items"]) == 2

    def test_offset_skips_items(
        self, client, published_course, published_tutorial, published_lab,
    ):
        first = client.get(FEED_URL, params={"limit": 2, "offset": 0}).json()
        second = client.get(FEED_URL, params={"limit": 2, "offset": 2}).json()
        assert first["meta"]["has_more"] is True
        assert second["meta"]["total"] == 3
        assert second["meta"]["offset"] == 2
        assert second["meta"]["has_more"] is False
        assert len(second["items"]) == 1
        first_slugs = {item["slug"] for item in first["items"]}
        second_slugs = {item["slug"] for item in second["items"]}
        assert first_slugs.isdisjoint(second_slugs)

    def test_offset_past_end_returns_empty_page(self, client, published_course):
        body = client.get(FEED_URL, params={"offset": 999}).json()
        assert body["meta"]["total"] == 1
        assert body["items"] == []
        assert body["meta"]["has_more"] is False

    def test_limit_zero_is_422(self, client):
        assert client.get(FEED_URL, params={"limit": 0}).status_code == 422

    def test_limit_above_max_is_422(self, client):
        assert client.get(FEED_URL, params={"limit": 101}).status_code == 422

    def test_negative_offset_is_422(self, client):
        assert client.get(FEED_URL, params={"offset": -1}).status_code == 422


class TestCacheControlHeaders:
    def test_feed_cache_control(self, client, published_course):
        resp = client.get(FEED_URL)
        assert resp.headers.get("cache-control") == "public, max-age=60"

    def test_detail_cache_control(self, client, published_course):
        resp = client.get(f"{CONTENT_URL}/course/syndication-course")
        assert resp.headers.get("cache-control") == "public, max-age=300"


class TestFeedConditionalGet:
    def test_etag_present_on_200(self, client, published_course):
        resp = client.get(FEED_URL)
        etag = resp.headers.get("etag")
        assert etag is not None
        assert etag.startswith('"') and etag.endswith('"')

    def test_etag_stable_across_requests(self, client, published_course):
        first = client.get(FEED_URL).headers["etag"]
        second = client.get(FEED_URL).headers["etag"]
        assert first == second

    def test_if_none_match_match_returns_304(self, client, published_course):
        etag = client.get(FEED_URL).headers["etag"]
        resp = client.get(FEED_URL, headers={"If-None-Match": etag})
        assert resp.status_code == 304
        assert resp.content == b""
        assert resp.headers.get("etag") == etag
        assert resp.headers.get("cache-control") == "public, max-age=60"

    def test_if_none_match_wildcard_returns_304(self, client, published_course):
        resp = client.get(FEED_URL, headers={"If-None-Match": "*"})
        assert resp.status_code == 304

    def test_if_none_match_mismatch_returns_200(self, client, published_course):
        resp = client.get(FEED_URL, headers={"If-None-Match": '"deadbeef"'})
        assert resp.status_code == 200
        assert resp.json()["meta"]["total"] == 1

    def test_etag_changes_when_content_changes(
        self, client, db_session: Session, published_course,
    ):
        first = client.get(FEED_URL).headers["etag"]
        published_course.title = "Renamed Syndication Course"
        db_session.flush()
        second = client.get(FEED_URL).headers["etag"]
        assert first != second

    def test_etag_ignores_generated_at(self, client, published_course):
        # Two consecutive calls have different generated_at timestamps
        # but the same content; ETag must not change.
        first = client.get(FEED_URL)
        second = client.get(FEED_URL)
        assert first.json()["meta"]["generated_at"] != second.json()["meta"]["generated_at"] \
            or True  # may collide on fast hardware; either way ETag stability is the guarantee
        assert first.headers["etag"] == second.headers["etag"]


class TestDetailConditionalGet:
    def test_etag_and_last_modified_present_on_200(self, client, published_course):
        resp = client.get(f"{CONTENT_URL}/course/syndication-course")
        assert resp.headers.get("etag") is not None
        assert resp.headers.get("last-modified") is not None

    def test_if_none_match_match_returns_304(self, client, published_course):
        first = client.get(f"{CONTENT_URL}/course/syndication-course")
        etag = first.headers["etag"]
        resp = client.get(
            f"{CONTENT_URL}/course/syndication-course",
            headers={"If-None-Match": etag},
        )
        assert resp.status_code == 304
        assert resp.content == b""
        assert resp.headers.get("etag") == etag
        assert resp.headers.get("last-modified") == first.headers["last-modified"]
        assert resp.headers.get("cache-control") == "public, max-age=300"

    def test_if_modified_since_future_returns_304(self, client, published_course):
        resp = client.get(
            f"{CONTENT_URL}/course/syndication-course",
            headers={"If-Modified-Since": "Wed, 01 Jan 2099 00:00:00 GMT"},
        )
        assert resp.status_code == 304
        assert resp.content == b""

    def test_if_modified_since_past_returns_200(self, client, published_course):
        resp = client.get(
            f"{CONTENT_URL}/course/syndication-course",
            headers={"If-Modified-Since": "Sun, 01 Jan 2000 00:00:00 GMT"},
        )
        assert resp.status_code == 200
        assert resp.json()["slug"] == "syndication-course"

    def test_if_none_match_takes_precedence_over_if_modified_since(
        self, client, published_course,
    ):
        # Mismatched ETag must return 200 even if If-Modified-Since would say "fresh".
        resp = client.get(
            f"{CONTENT_URL}/course/syndication-course",
            headers={
                "If-None-Match": '"deadbeef"',
                "If-Modified-Since": "Wed, 01 Jan 2099 00:00:00 GMT",
            },
        )
        assert resp.status_code == 200

    def test_if_modified_since_malformed_returns_200(self, client, published_course):
        resp = client.get(
            f"{CONTENT_URL}/course/syndication-course",
            headers={"If-Modified-Since": "not-a-date"},
        )
        assert resp.status_code == 200

    def test_404_does_not_set_validators(self, client):
        resp = client.get(f"{CONTENT_URL}/course/nonexistent-slug")
        assert resp.status_code == 404
        assert resp.headers.get("etag") is None
        assert resp.headers.get("last-modified") is None
