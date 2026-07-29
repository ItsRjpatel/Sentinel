import logging
import time
import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("app.middleware.logging")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = str(uuid.uuid4())
        # Attach request_id to request state
        request.state.request_id = request_id

        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Duration: {process_time:.4f}s",
                extra={"request_id": request_id},
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} "
                f"- Status: 500 "
                f"- Duration: {process_time:.4f}s - Error: {str(exc)}",
                extra={"request_id": request_id},
            )
            raise exc


def add_logging_middleware(app: FastAPI) -> None:
    """Add request logging middleware."""
    app.add_middleware(RequestLoggingMiddleware)
