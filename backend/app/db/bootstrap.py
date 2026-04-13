from textwrap import dedent
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Course, Lab, LearningPath, Tutorial
from app.models.content import ContentKind
from app.models.learning_path import LearningPathItem


def md(value: str) -> str:
    return dedent(value).strip()


CONTENT_SEED_DATA: dict[type[Course] | type[Tutorial] | type[Lab], list[dict[str, Any]]] = {
    Course: [
        {
            "slug": "python-fastapi-foundations",
            "title": "Python and FastAPI Foundations",
            "description": "Build a production-style Python API service with routing, validation, persistence, and clean delivery patterns.",
            "body_markdown": md(
                """
                # Python and FastAPI Foundations

                FastAPI works well when you treat it like a product backend, not just a quick demo server.

                ## In this course

                - model API resources cleanly
                - validate requests with Pydantic
                - structure a service layer for maintainability
                - ship an API that feels production-minded

                ## What learners should leave with

                By the end of this course, a developer should be able to stand up a small service, connect it to a database, and reason about how the codebase should grow over time.

                ## Why it matters

                Developer platforms often start with a single internal API. The teams that move quickly are the ones that establish predictable structure early.
                """
            ),
            "difficulty": "beginner",
            "estimated_minutes": 120,
            "tags": ["python", "fastapi", "apis", "backend"],
            "status": "published",
            "author": "LearnMesh Editorial",
            "content_type": ContentKind.course.value,
        },
        {
            "slug": "docker-for-app-developers",
            "title": "Docker for App Developers",
            "description": "Learn the container basics developers actually use for local setup, packaging, and repeatable service delivery.",
            "body_markdown": md(
                """
                # Docker for App Developers

                Docker is most useful when it reduces setup friction and makes service behavior predictable across machines.

                ## Core themes

                - image layers and build caching
                - development vs production container workflows
                - Compose as a local platform tool
                - debugging the boundary between host and container

                ## Practical outcome

                Learners finish with a clear mental model for turning a local service into something teammates can run with minimal onboarding pain.
                """
            ),
            "difficulty": "beginner",
            "estimated_minutes": 90,
            "tags": ["docker", "containers", "devops", "local-dev"],
            "status": "published",
            "author": "Avery Cole",
            "content_type": ContentKind.course.value,
        },
        {
            "slug": "kubernetes-intro-for-developers",
            "title": "Kubernetes Intro for Developers",
            "description": "A practical introduction to the Kubernetes concepts application engineers run into when software leaves local development.",
            "body_markdown": md(
                """
                # Kubernetes Intro for Developers

                This course is designed for developers who need platform fluency, not cluster-admin depth.

                ## Focus areas

                - pods, deployments, and services
                - what manifests are really describing
                - how application configuration changes in a cluster
                - where teams commonly get lost in the handoff to platform engineering

                ## Result

                Learners should feel comfortable reading basic manifests and understanding how an application is represented inside a Kubernetes environment.
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 105,
            "tags": ["kubernetes", "cloud-native", "containers", "platform"],
            "status": "published",
            "author": "Nina Brooks",
            "content_type": ContentKind.course.value,
        },
        {
            "slug": "llm-product-fundamentals",
            "title": "LLM Product Fundamentals",
            "description": "Understand the building blocks behind prompt-based applications, evaluation loops, and responsible product framing.",
            "body_markdown": md(
                """
                # LLM Product Fundamentals

                Large language models are most useful when developers know how to frame tasks, establish constraints, and evaluate behavior.

                ## Topics covered

                - prompts, context, and instruction design
                - evaluation as a product discipline
                - structured outputs and failure modes
                - where orchestration helps and where it only adds noise

                ## Takeaway

                This course gives learners a strong conceptual base before they start building AI-adjacent workflows into real products.
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 110,
            "tags": ["llm", "prompts", "evaluation", "ai"],
            "status": "published",
            "author": "Sana Malik",
            "content_type": ContentKind.course.value,
        },
        {
            "slug": "react-interface-patterns-for-dev-tools",
            "title": "React Interface Patterns for Dev Tools",
            "description": "Design clearer developer-facing interfaces with strong information hierarchy, progressive disclosure, and practical state management.",
            "body_markdown": md(
                """
                # React Interface Patterns for Dev Tools

                Developer products benefit from interfaces that reduce cognitive overhead and reward scanning.

                ## In this course

                - structure information-heavy layouts
                - design list-to-detail experiences
                - treat loading and empty states as product surfaces
                - make filters and metadata feel useful instead of ornamental

                ## Product framing

                Good frontend polish for technical tools is not decoration. It directly affects comprehension, trust, and speed.
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 100,
            "tags": ["react", "typescript", "ui", "frontend"],
            "status": "published",
            "author": "Maya Chen",
            "content_type": ContentKind.course.value,
        },
    ],
    Tutorial: [
        {
            "slug": "build-crud-api-fastapi-postgres",
            "title": "Build a CRUD API with FastAPI and PostgreSQL",
            "description": "Create a clean FastAPI resource with SQLAlchemy persistence, validation, and OpenAPI-friendly responses.",
            "body_markdown": md(
                """
                # Build a CRUD API with FastAPI and PostgreSQL

                This tutorial walks through a single resource from model to route.

                ## Steps

                1. define a SQLAlchemy model
                2. create Pydantic schemas
                3. wire up database sessions
                4. expose list, detail, create, update, and delete endpoints

                ## What to watch for

                Keep naming consistent and avoid pushing too much logic into route handlers.
                """
            ),
            "difficulty": "beginner",
            "estimated_minutes": 30,
            "tags": ["fastapi", "postgresql", "rest", "python"],
            "status": "published",
            "author": "Jordan Lee",
            "content_type": ContentKind.tutorial.value,
        },
        {
            "slug": "compose-your-local-dev-stack",
            "title": "Compose Your Local Dev Stack",
            "description": "Use Docker Compose to stand up a realistic service dependency graph for local product development.",
            "body_markdown": md(
                """
                # Compose Your Local Dev Stack

                Local platform quality matters. Teams move faster when their setup is reproducible.

                ## Tutorial outcomes

                - define services clearly
                - manage shared environment variables
                - expose only the ports a developer needs
                - make the stack obvious enough for a new teammate to run in minutes
                """
            ),
            "difficulty": "beginner",
            "estimated_minutes": 20,
            "tags": ["docker", "compose", "local-dev", "platform"],
            "status": "published",
            "author": "Avery Cole",
            "content_type": ContentKind.tutorial.value,
        },
        {
            "slug": "render-markdown-in-react-vite",
            "title": "Render Markdown Cleanly in React + Vite",
            "description": "Turn markdown into a polished reading experience inside a React product surface.",
            "body_markdown": md(
                """
                # Render Markdown Cleanly in React + Vite

                Markdown support becomes much more convincing when the surrounding UI feels intentional.

                ## Focus

                - select a renderer with a predictable API
                - style headings, lists, code blocks, and quotes
                - keep long-form content readable on wide and narrow layouts
                - avoid turning documentation views into plain text dumps
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 25,
            "tags": ["react", "vite", "markdown", "ui"],
            "status": "published",
            "author": "Maya Chen",
            "content_type": ContentKind.tutorial.value,
        },
        {
            "slug": "ground-llm-prompts-with-structured-context",
            "title": "Ground LLM Prompts with Structured Context",
            "description": "Learn a simple pattern for making prompt inputs more explicit, testable, and reusable.",
            "body_markdown": md(
                """
                # Ground LLM Prompts with Structured Context

                Prompt quality improves when context is organized before it is passed to a model.

                ## The pattern

                - separate instructions from data
                - define explicit output expectations
                - keep reference context bounded and purposeful
                - evaluate examples before scaling up usage
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 35,
            "tags": ["llm", "prompts", "context", "ai"],
            "status": "published",
            "author": "Sana Malik",
            "content_type": ContentKind.tutorial.value,
        },
        {
            "slug": "read-kubernetes-deployment-manifests",
            "title": "Read Kubernetes Deployment Manifests",
            "description": "Build confidence reading the Kubernetes YAML developers most commonly encounter.",
            "body_markdown": md(
                """
                # Read Kubernetes Deployment Manifests

                You do not need to memorize every Kubernetes field to become effective.

                ## Look for

                - the container image
                - the replica count
                - environment configuration
                - exposed ports and service linkage

                The goal is operational fluency, not platform specialization.
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 28,
            "tags": ["kubernetes", "yaml", "cloud-native", "platform"],
            "status": "published",
            "author": "Nina Brooks",
            "content_type": ContentKind.tutorial.value,
        },
    ],
    Lab: [
        {
            "slug": "containerize-fastapi-service",
            "title": "Containerize a FastAPI Service",
            "description": "Package a FastAPI application, connect it to a database container, and verify the local runtime loop.",
            "body_markdown": md(
                """
                # Containerize a FastAPI Service

                This lab focuses on the practical mechanics of shipping a local backend as a containerized unit.

                ## Lab tasks

                - write a backend Dockerfile
                - connect the app to PostgreSQL through Compose
                - validate health and seeded data
                - debug the most common startup failures
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "tags": ["docker", "fastapi", "containers", "postgresql"],
            "status": "published",
            "author": "Avery Cole",
            "content_type": ContentKind.lab.value,
        },
        {
            "slug": "trace-react-fastapi-request-flow",
            "title": "Trace a React to FastAPI Request Flow",
            "description": "Follow a request from the browser to the backend and back again to understand the product surface end to end.",
            "body_markdown": md(
                """
                # Trace a React to FastAPI Request Flow

                Great product teams understand what each layer is doing, especially when the UI starts to feel slow or ambiguous.

                ## Lab tasks

                - inspect a fetch call in the browser
                - map the route to a backend endpoint
                - confirm the response shape
                - fix a presentational issue without changing the whole architecture
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 40,
            "tags": ["react", "fastapi", "debugging", "frontend"],
            "status": "published",
            "author": "Maya Chen",
            "content_type": ContentKind.lab.value,
        },
        {
            "slug": "kubernetes-manifest-reading-lab",
            "title": "Kubernetes Manifest Reading Lab",
            "description": "Practice reading deployment and service manifests the way an application team would during a platform handoff.",
            "body_markdown": md(
                """
                # Kubernetes Manifest Reading Lab

                This lab keeps the focus on application understanding rather than cluster operations.

                ## Lab tasks

                - identify runtime configuration
                - match services to deployments
                - reason about scaling and exposure settings
                - explain what would need to change for a new environment
                """
            ),
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "tags": ["kubernetes", "yaml", "cloud-native", "devops"],
            "status": "published",
            "author": "Nina Brooks",
            "content_type": ContentKind.lab.value,
        },
        {
            "slug": "evaluate-prompts-with-rubrics",
            "title": "Evaluate Prompts with Rubrics",
            "description": "Use lightweight evaluation criteria to compare prompt behavior and make iteration more disciplined.",
            "body_markdown": md(
                """
                # Evaluate Prompts with Rubrics

                Prompt iteration becomes much more effective when teams agree on how they will judge quality.

                ## Lab tasks

                - define a compact rubric
                - compare multiple prompt variants
                - record expected failure modes
                - turn qualitative observations into repeatable team practice
                """
            ),
            "difficulty": "advanced",
            "estimated_minutes": 55,
            "tags": ["llm", "evaluation", "experimentation", "prompts"],
            "status": "published",
            "author": "Sana Malik",
            "content_type": ContentKind.lab.value,
        },
    ],
}

LEARNING_PATH_SEED_DATA: list[dict[str, Any]] = [
    {
        "slug": "backend-api-starter-path",
        "title": "Backend API Starter Path",
        "description": "A practical sequence for developers moving from API foundations into containerized local delivery.",
        "ordered_content": [
            {"content_type": "course", "slug": "python-fastapi-foundations"},
            {"content_type": "tutorial", "slug": "build-crud-api-fastapi-postgres"},
            {"content_type": "tutorial", "slug": "compose-your-local-dev-stack"},
            {"content_type": "lab", "slug": "containerize-fastapi-service"},
        ],
    },
    {
        "slug": "frontend-learning-experience-path",
        "title": "Frontend Learning Experience Path",
        "description": "A UI-focused sequence for turning data-heavy developer content into a polished product experience.",
        "ordered_content": [
            {"content_type": "course", "slug": "react-interface-patterns-for-dev-tools"},
            {"content_type": "tutorial", "slug": "render-markdown-in-react-vite"},
            {"content_type": "lab", "slug": "trace-react-fastapi-request-flow"},
        ],
    },
    {
        "slug": "cloud-native-developer-ramp",
        "title": "Cloud-Native Developer Ramp",
        "description": "Learn the container and Kubernetes concepts application engineers need before deeper platform work.",
        "ordered_content": [
            {"content_type": "course", "slug": "docker-for-app-developers"},
            {"content_type": "course", "slug": "kubernetes-intro-for-developers"},
            {"content_type": "tutorial", "slug": "read-kubernetes-deployment-manifests"},
            {"content_type": "lab", "slug": "kubernetes-manifest-reading-lab"},
        ],
    },
    {
        "slug": "llm-builder-foundations",
        "title": "LLM Builder Foundations",
        "description": "A grounded path for developers who want to understand prompts, context design, and simple evaluation loops.",
        "ordered_content": [
            {"content_type": "course", "slug": "llm-product-fundamentals"},
            {"content_type": "tutorial", "slug": "ground-llm-prompts-with-structured-context"},
            {"content_type": "lab", "slug": "evaluate-prompts-with-rubrics"},
        ],
    },
]


def bootstrap_database(seed: bool = True) -> None:
    if not seed:
        return

    with SessionLocal() as session:
        seed_database(session)


def seed_database(session: Session) -> None:
    content_index: dict[tuple[str, str], Course | Tutorial | Lab] = {}

    for model, items in CONTENT_SEED_DATA.items():
        for payload in items:
            item = upsert_content_item(session, model, payload)
            content_index[(payload["content_type"], payload["slug"])] = item

    for path_payload in LEARNING_PATH_SEED_DATA:
        learning_path = session.scalar(
            select(LearningPath).where(LearningPath.slug == path_payload["slug"])
        )
        if learning_path is None:
            learning_path = LearningPath(
                slug=path_payload["slug"],
                title=path_payload["title"],
                description=path_payload["description"],
            )
            session.add(learning_path)
            session.flush()
        else:
            learning_path.title = path_payload["title"]
            learning_path.description = path_payload["description"]

        replace_learning_path_items(
            session,
            learning_path,
            path_payload["ordered_content"],
            content_index,
        )

    session.commit()


def upsert_content_item(
    session: Session,
    model: type[Course] | type[Tutorial] | type[Lab],
    payload: dict[str, Any],
) -> Course | Tutorial | Lab:
    item = session.scalar(select(model).where(model.slug == payload["slug"]))

    if item is None:
        item = model(**payload)
        session.add(item)
    else:
        for field, value in payload.items():
            setattr(item, field, value)

    session.flush()
    return item


def replace_learning_path_items(
    session: Session,
    learning_path: LearningPath,
    ordered_content: list[dict[str, str]],
    content_index: dict[tuple[str, str], Course | Tutorial | Lab],
) -> None:
    learning_path.items.clear()
    session.flush()

    for position, reference in enumerate(ordered_content, start=1):
        content_item = content_index[(reference["content_type"], reference["slug"])]
        learning_path.items.append(
            LearningPathItem(
                position=position,
                content_type=content_item.content_type,
                content_id=content_item.id,
                content_slug=content_item.slug,
                content_title=content_item.title,
            )
        )
