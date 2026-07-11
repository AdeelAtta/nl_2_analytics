from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("role") not in ("admin", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return {
        "success": True,
        "data": {
            "total_queries": 0,
            "active_connections": 0,
            "total_tenants": 0,
            "total_tables": 0,
            "status": "healthy",
        },
    }


@router.get("/health")
async def admin_health(
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    db = redis_check = qdrant = False
    try:
        from app.core.database import check_db_health, check_qdrant_health, check_redis_health
        db = await check_db_health()
        redis_check = await check_redis_health()
        qdrant = await check_qdrant_health()
    except Exception:
        pass
    all_ok = db and redis_check and qdrant
    return {
        "success": True,
        "data": {
            "status": "ok" if all_ok else "degraded",
            "database": "healthy" if db else "unhealthy",
            "redis": "healthy" if redis_check else "unhealthy",
            "qdrant": "healthy" if qdrant else "unhealthy",
        },
    }
