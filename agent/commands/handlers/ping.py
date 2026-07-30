import platform
import socket
from datetime import datetime, timezone

def execute(command: dict) -> dict:
    """Handles the PING command."""
    return {
        "hostname": socket.gethostname(),
        "time": datetime.now(timezone.utc).isoformat(),
        "success": True
    }
