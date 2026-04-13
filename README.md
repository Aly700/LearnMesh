# LearnMesh

LearnMesh is a full-stack developer learning and content platform designed to feel like an app-store-style LMS for technical education. Phase 2 extends the Phase 1 MVP with richer browsing, individual detail pages, markdown-rendered lessons, stronger learning-path UX, and a more polished product surface that is easier to demo on GitHub or in an interview.

## Why this project exists

Developer education platforms often need to manage multiple content shapes at once: structured courses, quick tutorials, hands-on labs, and curated learning paths. LearnMesh exists to show how those building blocks can be modeled cleanly in a practical product foundation without jumping straight into enterprise-scale complexity.

## Phase 2 product experience

- Browse a unified catalog across courses, tutorials, and labs
- Open individual content detail pages with long-form markdown content
- Explore richer learning paths with ordered steps and quick navigation
- Filter content by difficulty, tags, status, and content type where appropriate
- Demo a more credible developer education platform instead of a plain CRUD UI

## Architecture summary

- `backend/`: FastAPI service, SQLAlchemy models, seed/bootstrap logic, and REST APIs
- `frontend/`: React + TypeScript + Vite application for dashboard, explore, list, detail, and learning-path views
- `infra/docker/`: Dockerfiles plus Compose stack for backend, frontend, and PostgreSQL
- `docs/`: Architecture, API, and content-model documentation

See [docs/architecture.md](docs/architecture.md), [docs/content-model.md](docs/content-model.md), and [docs/api.md](docs/api.md) for deeper detail.

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Frontend: React, TypeScript, Vite, React Router
- Content rendering: React Markdown
- Database: PostgreSQL
- Infra: Docker Compose
- Tooling: Seed script and local setup script

## Folder structure

```text
learnmesh/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── pages/
│   └── .env.example
├── docs/
├── infra/docker/
└── scripts/
```

## Local setup

If you are upgrading from the Phase 1 schema, recreate your local database before running Phase 2. This phase adds long-form markdown fields and richer seeded content.

Docker volume reset:

```bash
docker compose -f infra/docker/docker-compose.yml down -v
```

Local Postgres reset:

```bash
dropdb learnmesh
createdb learnmesh
```

### 1. Start PostgreSQL

Use a local Postgres instance or run the Docker Compose stack. The default local connection string used by the backend is:

```text
postgresql+psycopg://learnmesh:learnmesh@localhost:5432/learnmesh
```

### 2. Backend

```bash
cd backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Schema is managed exclusively by Alembic. On a brand-new database run `alembic upgrade head` before the first server start. If you already have a Phase 2 database from before Alembic landed, stamp it once with `alembic stamp 0001_baseline_phase_2` instead of running `upgrade` — this marks the existing tables as already at the baseline without re-running DDL.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

The app will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

## Docker setup

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

## API overview

Base URL: `http://localhost:8000/api/v1`

- `GET /health`
- `GET /catalog` for unified content browsing
- CRUD for `courses`, plus `GET /courses/slug/{slug}`
- CRUD for `tutorials`, plus `GET /tutorials/slug/{slug}`
- CRUD for `labs`, plus `GET /labs/slug/{slug}`
- CRUD for `learning-paths`, plus `GET /learning-paths/slug/{slug}`
- Lightweight filtering on content lists via `difficulty`, `tags`, `status`, and `content_type`

The OpenAPI schema is intentionally kept clean so the docs page is useful for local exploration and manual API testing.

## Seed data

Phase 2 ships with a broader seeded catalog across:

- Python API development
- Docker basics
- Kubernetes intro
- LLM fundamentals
- React and markdown-driven product UI

The backend bootstraps tables on startup and seeds the database when `AUTO_SEED=true`.

To seed explicitly:

```bash
cd backend
source .venv/bin/activate
python -m app.seed
```

## Suggested screenshots

For a stronger GitHub README or resume project showcase, capture:

- the dashboard hero and featured content sections
- the Explore page with filters applied
- a content detail page showing markdown rendering
- a learning path detail page with the ordered timeline

## Roadmap

### Phase 1

- Local MVP with CRUD APIs, catalog UI, seed data, and Docker support

### Phase 2

- Detail pages, markdown rendering, richer browsing, and stronger learning-path UX

### Phase 3

- Auth and role-based access
- Progress tracking and enrollment primitives
- Search and metadata enrichment
- Editorial/admin authoring workflows
