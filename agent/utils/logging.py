import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Custom logging Formatter that outputs log records as single-line JSON structures."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "process_id": record.process,
            "thread_name": record.threadName,
        }
        
        # Include correlation or request ID context
        for attr in ("request_id", "correlation_id"):
            if hasattr(record, attr):
                log_payload[attr] = getattr(record, attr)
            else:
                log_payload[attr] = "N/A"
                
        # Format exceptions if present
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_payload)


def setup_logging(log_file: Path, log_level: str = "INFO") -> None:
    """Configures the root logger with JSON format, rotating file outputs, and console outputs."""
    # Ensure logs folder exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # File Handler: 5MB size rotation, keeping 5 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Console Handler for development environment
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
