from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """Returns application health and environment info."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment,
    }
