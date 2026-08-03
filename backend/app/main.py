from fastapi import FastAPI

from app.common.middleware import setup_middlewares
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.lifespan import lifespan
from app.modules.auth.router import router as auth_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.endpoints.router import router as endpoints_router
from app.modules.inventory.router import router as inventory_router
from app.modules.commands.router import router as commands_router, endpoint_router as commands_endpoint_router
from app.modules.alerts.router import router as alerts_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.audit.router import router as audit_router
from app.modules.users.router import router as users_router
from app.modules.settings.router import router as settings_router
from app.modules.reports.router import router as reports_router


from app.modules.groups.router import router as groups_router
from app.modules.policies.router import router as policies_router
from app.modules.schedules.router import router as schedules_router
from app.modules.notifications.router import router as notifications_router
from app.modules.search.router import router as search_router


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
    app.include_router(users_router, prefix=settings.API_PREFIX)
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(endpoints_router, prefix=settings.API_PREFIX)
    app.include_router(inventory_router, prefix=settings.API_PREFIX)
    app.include_router(commands_router, prefix=settings.API_PREFIX)
    app.include_router(commands_endpoint_router, prefix=settings.API_PREFIX)
    app.include_router(alerts_router, prefix=settings.API_PREFIX)
    app.include_router(dashboard_router, prefix=settings.API_PREFIX)
    app.include_router(audit_router, prefix=settings.API_PREFIX)
    app.include_router(settings_router, prefix=settings.API_PREFIX)
    app.include_router(reports_router, prefix=settings.API_PREFIX)
    app.include_router(groups_router, prefix=settings.API_PREFIX)
    app.include_router(policies_router, prefix=settings.API_PREFIX)
    app.include_router(schedules_router, prefix=settings.API_PREFIX)
    app.include_router(notifications_router, prefix=settings.API_PREFIX)
    app.include_router(search_router, prefix=settings.API_PREFIX)
    
    from app.modules.commands.websocket import router as ws_commands_router
    app.include_router(ws_commands_router)

    return app


app = create_app()
