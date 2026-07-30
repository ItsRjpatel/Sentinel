from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

def get_utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

class WebSocketEvent(BaseModel):
    """
    Common schema for WebSocket events.
    """
    event_type: str = Field(..., description="The type of the event (e.g., COMMAND_QUEUED)")
    timestamp: str = Field(default_factory=get_utc_now_iso, description="ISO8601 timestamp")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique correlation ID for this event payload")
    user: Optional[str] = Field(None, description="Username of the user who initiated the action, if applicable")
    endpoint_id: Optional[str] = Field(None, description="Target endpoint ID, if applicable")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific payload data")
