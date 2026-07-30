import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """
    Configures structured logging for the application.
    Sets up a console handler and a rotating file handler.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Format includes a request ID placeholder that can be injected via filter/middleware
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
    )
    date_format = "%Y-%m-%dT%H:%M:%S%z"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Rotating File Handler (10 MB max size, 5 backups)
    file_handler = RotatingFileHandler(
        log_dir / "sentinel.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Create a filter to inject default request_id if not present
    class RequestIdFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "request_id"):
                record.request_id = "N/A"
            return True

    req_id_filter = RequestIdFilter()
    console_handler.addFilter(req_id_filter)
    file_handler.addFilter(req_id_filter)

    # Apply configuration to root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Configure uvicorn loggers to use the same format
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = root_logger.handlers
        uv_logger.addFilter(RequestIdFilter())
        uv_logger.propagate = False
