"""Health and readiness check endpoints."""

from fastapi import APIRouter

from src.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="healthy", version="0.1.0")


@router.get("/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """Return service readiness status."""
    return HealthResponse(status="ready", version="0.1.0")
