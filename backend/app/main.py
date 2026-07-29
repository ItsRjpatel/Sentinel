from fastapi import FastAPI

from app.common.middleware import setup_middlewares
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.lifespan import lifespan
from app.modules.auth.router import router as auth_router
from app.modules.monitoring.router import router as monitoring_router


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Middlewares
    setup_middlewares(app)

    # Exception Handlers
    setup_exception_handlers(app)

    # Routers
    app.include_router(monitoring_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
