import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.logger import setup_logging
from app.db.database import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events securely and cleanly.
    """
    # --- Startup ---
    setup_logging()
    logger.info("Initializing Sentinel Backend...")
    logger.info("Connecting to database...")

    from app.core.websocket.bridge import setup_websocket_bridge
    from app.core.websocket.manager import connection_manager
    import asyncio
    
    setup_websocket_bridge()
    cleanup_task = asyncio.create_task(connection_manager.cleanup_dead_connections())

    yield
    
    cleanup_task.cancel()

    # --- Shutdown ---
    logger.info("Shutting down Sentinel Backend...")
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Shutdown complete.")
