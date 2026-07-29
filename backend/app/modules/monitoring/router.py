from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

from app.core.config import settings
from app.core.constants import (
    STATUS_DB_CONNECTED,
    STATUS_DB_DISCONNECTED,
    STATUS_HEALTHY,
    STATUS_UNHEALTHY,
)
from app.db.session import get_db

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Health check endpoint for the application.
    """
    database_status = STATUS_DB_DISCONNECTED
    app_status = STATUS_UNHEALTHY

    try:
        # Simple ping to the database
        await db.execute(text("SELECT 1"))
        database_status = STATUS_DB_CONNECTED
        app_status = STATUS_HEALTHY
    except Exception:
        pass

    return {
        "status": app_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": database_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
