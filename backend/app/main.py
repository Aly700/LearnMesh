from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.bootstrap import bootstrap_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_database(seed=settings.auto_seed)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "LearnMesh is a developer learning platform MVP for courses, tutorials, "
        "labs, and learning paths."
    ),
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_tags=[
        {"name": "Health", "description": "Service and database readiness checks."},
        {"name": "Catalog", "description": "Unified content browsing across all content types."},
        {"name": "Courses", "description": "Developer course catalog endpoints."},
        {"name": "Tutorials", "description": "Hands-on tutorial catalog endpoints."},
        {"name": "Labs", "description": "Lab catalog endpoints."},
        {"name": "Learning Paths", "description": "Ordered curriculum collections."},
    ],
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
