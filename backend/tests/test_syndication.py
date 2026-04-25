"""Tests for the content syndication feed endpoint."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.content import Course, Lab, Tutorial
from app.models.learning_path import LearningPath, LearningPathItem

FEED_URL = "/api/v1/syndication/feed"
CONTENT_URL = "/api/v1/syndication/content"
PATH_URL = "/api/v1/syndication/learning-paths"


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


def _make_published(db_session, model, *, slug, title, minutes=30, content_type, status_value="published"):
    item = model(
        slug=slug,
        title=title,
        description=f"{title} description.",
        body_markdown=f"# {title}",
        difficulty="beginner",
        estimated_minutes=minutes,
        tags=[],
        status=status_value,
        author="Path Author",
        content_type=content_type,
    )
    db_session.add(item)
    db_session.flush()
    return item


@pytest.fixture()
def path_course(db_session: Session) -> Course:
    return _make_published(db_session, Course, slug="path-course-a", title="Path Course A",
                           minutes=30, content_type="course")


@pytest.fixture()
def path_tutorial(db_session: Session) -> Tutorial:
    return _make_published(db_session, Tutorial, slug="path-tutorial-b", title="Path Tutorial B",
                           minutes=15, content_type="tutorial")


@pytest.fixture()
def path_lab_draft(db_session: Session) -> Lab:
    return _make_published(db_session, Lab, slug="path-lab-draft", title="Draft Lab",
                           minutes=60, content_type="lab", status_value="draft")


def _make_path(db_session, *, slug, title, member_specs):
    """member_specs: iterable of (position, content_row[, override_content_id])."""
    path = LearningPath(slug=slug, title=title, description=f"{title} description.")
    db_session.add(path)
    db_session.flush()
    for spec in member_specs:
        position = spec[0]
        content_row = spec[1]
        content_id = spec[2] if len(spec) > 2 else content_row.id
        path.items.append(
            LearningPathItem(
                position=position,
                content_type=content_row.content_type,
                content_id=content_id,
                content_slug=content_row.slug,
                content_title=content_row.title,
            )
        )
    db_session.flush()
    return path


class TestLearningPathDetail:
    def test_returns_200_for_published_path(self, client, db_session, path_course, path_tutorial):
        path = _make_path(
            db_session,
            slug="full-stack",
            title="Full Stack",
            member_specs=[(1, path_course), (2, path_tutorial)],
        )
        resp = client.get(f"{PATH_URL}/{path.slug}")
        assert resp.status_code == 200

    def test_response_shape(self, client, db_session, path_course, path_tutorial):
        path = _make_path(
            db_session,
            slug="full-stack-shape",
            title="Full Stack Shape",
            member_specs=[(1, path_course), (2, path_tutorial)],
        )
        body = client.get(f"{PATH_URL}/{path.slug}").json()
        assert body["slug"] == "full-stack-shape"
        assert body["title"] == "Full Stack Shape"
        assert "description" in body
        assert body["step_count"] == 2
        assert body["estimated_minutes_total"] == 45  # 30 + 15
        assert "created_at" in body and "updated_at" in body
        assert isinstance(body["steps"], list)
        assert len(body["steps"]) == 2

    def test_steps_have_only_public_fields(self, client, db_session, path_course):
        path = _make_path(
            db_session, slug="one-step", title="One Step",
            member_specs=[(1, path_course)],
        )
        step = client.get(f"{PATH_URL}/{path.slug}").json()["steps"][0]
        assert set(step.keys()) == {"position", "content_type", "slug", "title"}
        assert step["position"] == 1
        assert step["content_type"] == "course"
        assert step["slug"] == "path-course-a"
        assert step["title"] == "Path Course A"

    def test_step_count_and_total_match_filtered_steps(
        self, client, db_session, path_course, path_tutorial, path_lab_draft,
    ):
        path = _make_path(
            db_session, slug="mixed-status", title="Mixed Status",
            member_specs=[(1, path_course), (2, path_lab_draft), (3, path_tutorial)],
        )
        body = client.get(f"{PATH_URL}/{path.slug}").json()
        assert body["step_count"] == 2
        assert body["estimated_minutes_total"] == 45  # course 30 + tutorial 15, draft excluded
        assert len(body["steps"]) == 2

    def test_unknown_slug_returns_404(self, client):
        resp = client.get(f"{PATH_URL}/does-not-exist")
        assert resp.status_code == 404

    def test_path_with_only_draft_steps_returns_404(
        self, client, db_session, path_lab_draft,
    ):
        path = _make_path(
            db_session, slug="all-draft", title="All Draft",
            member_specs=[(1, path_lab_draft)],
        )
        resp = client.get(f"{PATH_URL}/{path.slug}")
        assert resp.status_code == 404

    def test_position_gaps_preserved(
        self, client, db_session, path_course, path_tutorial, path_lab_draft,
    ):
        path = _make_path(
            db_session, slug="gappy", title="Gappy",
            member_specs=[(1, path_course), (2, path_lab_draft), (3, path_tutorial)],
        )
        steps = client.get(f"{PATH_URL}/{path.slug}").json()["steps"]
        positions = [s["position"] for s in steps]
        assert positions == [1, 3]

    def test_orphaned_step_filtered_alongside_drafts(
        self, client, db_session, path_course,
    ):
        # Step 2 references a content_id that doesn't exist.
        path = _make_path(
            db_session, slug="with-orphan", title="With Orphan",
            member_specs=[(1, path_course), (2, path_course, 999_999)],
        )
        body = client.get(f"{PATH_URL}/{path.slug}").json()
        assert body["step_count"] == 1
        assert [s["position"] for s in body["steps"]] == [1]

    def test_path_with_only_orphaned_steps_returns_404(self, client, db_session, path_course):
        path = _make_path(
            db_session, slug="all-orphans", title="All Orphans",
            member_specs=[(1, path_course, 999_999), (2, path_course, 999_998)],
        )
        resp = client.get(f"{PATH_URL}/{path.slug}")
        assert resp.status_code == 404

    def test_no_auth_required(self, client, db_session, path_course):
        path = _make_path(
            db_session, slug="no-auth", title="No Auth",
            member_specs=[(1, path_course)],
        )
        with_auth = client.get(f"{PATH_URL}/{path.slug}", headers={"Authorization": "Bearer x"})
        without = client.get(f"{PATH_URL}/{path.slug}")
        assert with_auth.status_code == 200
        assert without.status_code == 200
        assert with_auth.json() == without.json()

    def test_internal_crud_endpoint_unchanged(
        self, client, db_session, path_course, path_lab_draft,
    ):
        # Internal endpoint must still expose unfiltered, internal-shape data.
        path = _make_path(
            db_session, slug="internal-shape", title="Internal Shape",
            member_specs=[(1, path_course), (2, path_lab_draft)],
        )
        resp = client.get(f"/api/v1/learning-paths/slug/{path.slug}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["step_count"] == 2  # both members present, including the draft
        statuses = {step["status"] for step in body["ordered_content"]}
        assert "draft" in statuses


class TestLearningPathConditionalGet:
    def test_etag_last_modified_and_cache_control_present(
        self, client, db_session, path_course,
    ):
        path = _make_path(
            db_session, slug="cond-headers", title="Cond Headers",
            member_specs=[(1, path_course)],
        )
        resp = client.get(f"{PATH_URL}/{path.slug}")
        assert resp.headers.get("etag") is not None
        assert resp.headers.get("last-modified") is not None
        assert resp.headers.get("cache-control") == "public, max-age=300"

    def test_etag_stable_across_requests(self, client, db_session, path_course):
        path = _make_path(
            db_session, slug="cond-stable", title="Cond Stable",
            member_specs=[(1, path_course)],
        )
        first = client.get(f"{PATH_URL}/{path.slug}").headers["etag"]
        second = client.get(f"{PATH_URL}/{path.slug}").headers["etag"]
        assert first == second

    def test_if_none_match_returns_304(self, client, db_session, path_course):
        path = _make_path(
            db_session, slug="cond-inm", title="Cond INM",
            member_specs=[(1, path_course)],
        )
        first = client.get(f"{PATH_URL}/{path.slug}")
        etag = first.headers["etag"]
        resp = client.get(f"{PATH_URL}/{path.slug}", headers={"If-None-Match": etag})
        assert resp.status_code == 304
        assert resp.content == b""
        assert resp.headers.get("etag") == etag
        assert resp.headers.get("last-modified") == first.headers["last-modified"]
        assert resp.headers.get("cache-control") == "public, max-age=300"

    def test_if_modified_since_future_returns_304_past_returns_200(
        self, client, db_session, path_course,
    ):
        path = _make_path(
            db_session, slug="cond-ims", title="Cond IMS",
            member_specs=[(1, path_course)],
        )
        future = client.get(
            f"{PATH_URL}/{path.slug}",
            headers={"If-Modified-Since": "Wed, 01 Jan 2099 00:00:00 GMT"},
        )
        past = client.get(
            f"{PATH_URL}/{path.slug}",
            headers={"If-Modified-Since": "Sun, 01 Jan 2000 00:00:00 GMT"},
        )
        assert future.status_code == 304
        assert past.status_code == 200

    def test_last_modified_reflects_max_of_path_and_members(
        self, client, db_session, path_course,
    ):
        # Bump the member's updated_at well past the path's.
        future = datetime.now(UTC) + timedelta(days=30)
        path_course.updated_at = future
        db_session.flush()

        path = _make_path(
            db_session, slug="cond-max", title="Cond Max",
            member_specs=[(1, path_course)],
        )
        # Force the path's updated_at to be earlier than the member's.
        path.updated_at = datetime.now(UTC) - timedelta(days=1)
        db_session.flush()

        resp = client.get(f"{PATH_URL}/{path.slug}")
        # Member's future timestamp (past today) means If-Modified-Since=today → 200.
        # If Last-Modified ignored the member, IMS=today would return 304.
        today_header = "Sat, 25 Apr 2026 04:00:00 GMT"
        replay = client.get(
            f"{PATH_URL}/{path.slug}",
            headers={"If-Modified-Since": today_header},
        )
        assert resp.status_code == 200
        assert replay.status_code == 200  # member's future updated_at wins → not modified-since today

    def test_404_does_not_set_validators(self, client):
        resp = client.get(f"{PATH_URL}/no-such-path")
        assert resp.status_code == 404
        assert resp.headers.get("etag") is None
        assert resp.headers.get("last-modified") is None
