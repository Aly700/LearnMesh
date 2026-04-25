"""Tests for the weighted keyword search endpoint."""

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models.content import Course, Lab, Tutorial

SEARCH_URL = "/api/v1/search"


@pytest.fixture()
def seeded_content(db_session: Session) -> None:
    """Seed three published items + one draft with distinctive fields."""
    db_session.add_all(
        [
            Course(
                slug="docker-fundamentals",
                title="Docker Fundamentals",
                description="Learn containerization basics with Docker and Compose.",
                body_markdown="# Docker body",
                difficulty="beginner",
                estimated_minutes=60,
                tags=["docker", "containers"],
                status="published",
                author="Alice Example",
                content_type="course",
            ),
            Tutorial(
                slug="kubernetes-intro",
                title="Kubernetes Intro",
                description="A short intro to orchestration using Kubernetes.",
                body_markdown="# K8s body",
                difficulty="intermediate",
                estimated_minutes=30,
                tags=["kubernetes", "devops"],
                status="published",
                author="Bob Devops",
                content_type="tutorial",
            ),
            Lab(
                slug="python-apis-lab",
                title="Building Python APIs",
                description="Hands-on lab for FastAPI, covering routes and models.",
                body_markdown="# Python body",
                difficulty="intermediate",
                estimated_minutes=45,
                tags=["python", "fastapi"],
                status="published",
                author="Alice Example",
                content_type="lab",
            ),
            Course(
                slug="draft-docker-advanced",
                title="Advanced Docker",
                description="Draft advanced docker course; should NOT appear in search.",
                body_markdown="# Draft",
                difficulty="advanced",
                estimated_minutes=90,
                tags=["docker", "advanced"],
                status="draft",
                author="Carol Draft",
                content_type="course",
            ),
        ]
    )
    db_session.flush()


class TestSearchBasics:
    def test_empty_catalog_returns_zero_results(self, client: TestClient) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker"})
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"query": "docker", "total": 0, "results": []}

    def test_no_auth_required(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker"})
        assert resp.status_code == 200

    def test_missing_q_is_422(self, client: TestClient) -> None:
        resp = client.get(SEARCH_URL)
        assert resp.status_code == 422

    def test_empty_q_is_422(self, client: TestClient) -> None:
        resp = client.get(SEARCH_URL, params={"q": ""})
        assert resp.status_code == 422

    def test_single_char_q_is_422(self, client: TestClient) -> None:
        resp = client.get(SEARCH_URL, params={"q": "a"})
        assert resp.status_code == 422


class TestFieldMatching:
    def test_title_match(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "kubernetes"})
        body = resp.json()
        assert body["total"] == 1
        hit = body["results"][0]
        assert hit["slug"] == "kubernetes-intro"
        assert "title" in hit["matched_fields"]
        assert "tags" in hit["matched_fields"]
        assert hit["score"] > 0

    def test_description_only_match(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "orchestration"})
        body = resp.json()
        assert body["total"] == 1
        hit = body["results"][0]
        assert hit["slug"] == "kubernetes-intro"
        assert hit["matched_fields"] == ["description"]

    def test_tag_match(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "fastapi"})
        body = resp.json()
        assert body["total"] == 1
        hit = body["results"][0]
        assert hit["slug"] == "python-apis-lab"
        assert "tags" in hit["matched_fields"]

    def test_author_match(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "alice"})
        body = resp.json()
        assert body["total"] == 2
        for hit in body["results"]:
            assert "author" in hit["matched_fields"]

    def test_multi_field_match_collects_all_fields(
        self,
        client: TestClient,
        seeded_content: None,
    ) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker"})
        body = resp.json()
        assert body["total"] == 1
        hit = body["results"][0]
        assert hit["slug"] == "docker-fundamentals"
        assert set(hit["matched_fields"]) >= {"title", "tags", "description"}
        assert hit["matched_fields"] == sorted(
            hit["matched_fields"],
            key=["title", "tags", "description", "author"].index,
        )


class TestRankingAndFilters:
    def test_title_hit_outranks_description_hit(
        self,
        client: TestClient,
        seeded_content: None,
    ) -> None:
        resp = client.get(SEARCH_URL, params={"q": "python"})
        body = resp.json()
        assert body["total"] >= 1
        assert body["results"][0]["slug"] == "python-apis-lab"

    def test_draft_excluded(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "advanced"})
        body = resp.json()
        slugs = [r["slug"] for r in body["results"]]
        assert "draft-docker-advanced" not in slugs

    def test_content_type_filter(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker", "content_type": "tutorial"})
        body = resp.json()
        assert body["total"] == 0

        resp = client.get(SEARCH_URL, params={"q": "docker", "content_type": "course"})
        body = resp.json()
        assert body["total"] == 1
        assert body["results"][0]["content_type"] == "course"

    def test_invalid_content_type_is_422(
        self,
        client: TestClient,
        seeded_content: None,
    ) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker", "content_type": "bogus"})
        assert resp.status_code == 422

    def test_limit_caps_results(self, client: TestClient, seeded_content: None) -> None:
        resp = client.get(SEARCH_URL, params={"q": "a", "limit": 1})
        assert resp.status_code == 422  # q is min_length=2

        resp = client.get(SEARCH_URL, params={"q": "al", "limit": 1})
        assert resp.status_code == 200
        assert len(resp.json()["results"]) <= 1

    def test_limit_above_max_is_422(
        self,
        client: TestClient,
        seeded_content: None,
    ) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker", "limit": 51})
        assert resp.status_code == 422

    def test_result_has_score_and_matched_fields(
        self,
        client: TestClient,
        seeded_content: None,
    ) -> None:
        resp = client.get(SEARCH_URL, params={"q": "docker"})
        body = resp.json()
        assert body["query"] == "docker"
        assert body["total"] == len(body["results"])
        hit = body["results"][0]
        assert isinstance(hit["score"], (int, float))
        assert hit["score"] > 0
        assert isinstance(hit["matched_fields"], list)
        assert all(
            field in {"title", "tags", "description", "author"}
            for field in hit["matched_fields"]
        )
