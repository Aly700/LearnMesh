from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.catalog import router as catalog_router
from app.api.endpoints.courses import router as courses_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.labs import router as labs_router
from app.api.endpoints.learning_paths import router as learning_paths_router
from app.api.endpoints.progress import router as progress_router
from app.api.endpoints.search import router as search_router
from app.api.endpoints.syndication import router as syndication_router
from app.api.endpoints.tutorials import router as tutorials_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(catalog_router)
api_router.include_router(courses_router)
api_router.include_router(tutorials_router)
api_router.include_router(labs_router)
api_router.include_router(learning_paths_router)
api_router.include_router(progress_router)
api_router.include_router(search_router)
api_router.include_router(syndication_router)
