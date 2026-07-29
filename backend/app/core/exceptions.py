import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class SentinelException(Exception):
    """Base exception for all Sentinel domain errors."""

    pass


class AuthenticationError(SentinelException):
    """Base class for authentication errors."""

    pass


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT is malformed, invalid, or has a bad signature."""

    pass


class ExpiredTokenError(AuthenticationError):
    """Raised when a JWT has expired."""

    pass


class PermissionDeniedError(SentinelException):
    """Raised when a user attempts an action without required permissions."""

    pass


class InactiveUserError(SentinelException):
    """Raised when a deactivated user attempts to authenticate."""

    pass


class AccountLockedError(SentinelException):
    """Raised when a locked user attempts to authenticate."""

    pass


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers for the FastAPI application.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation Error", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(f"Unexpected error occurred on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal server error occurred."},
        )
