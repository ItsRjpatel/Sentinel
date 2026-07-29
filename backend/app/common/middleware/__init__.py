from fastapi import FastAPI

from .cors import add_cors_middleware
from .logging import add_logging_middleware
from .trusted_hosts import add_trusted_hosts_middleware


def setup_middlewares(app: FastAPI) -> None:
    """Register all middlewares for the FastAPI application."""
    # Note: Middlewares are executed in reverse order of addition.
    # The last middleware added is the first one to process the request.
    
    add_cors_middleware(app)
    add_trusted_hosts_middleware(app)
    add_logging_middleware(app)
