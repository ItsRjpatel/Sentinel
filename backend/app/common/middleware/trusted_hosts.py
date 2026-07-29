from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings


def add_trusted_hosts_middleware(app: FastAPI) -> None:
    """Add Trusted Hosts middleware to the application."""
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
