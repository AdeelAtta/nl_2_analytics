from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import (
    check_db_health,
    check_qdrant_health,
    check_redis_health,
)
from app.schemas.health import HealthResponse, VersionInfo

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()
    qdrant_ok = await check_qdrant_health()

    all_ok = db_ok and redis_ok and qdrant_ok

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        checks={
            "database": "healthy" if db_ok else "unhealthy",
            "redis": "healthy" if redis_ok else "unhealthy",
            "qdrant": "healthy" if qdrant_ok else "unhealthy",
        },
    )


@router.get("/version", response_model=VersionInfo)
async def version() -> VersionInfo:
    settings = get_settings()
    return VersionInfo(
        version=settings.app_version,
        build="development",
        environment=settings.environment,
    )
