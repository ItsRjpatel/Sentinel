import logging
from app.core.events.dispatcher import event_dispatcher
from app.core.websocket.manager import connection_manager
from app.core.websocket.schema import WebSocketEvent

logger = logging.getLogger(__name__)


async def handle_command_event(event_type: str, payload: dict):
    """
    Handles command events from the EventBus and broadcasts them to WebSockets.
    """
    endpoint_id = payload.get("endpoint_id")
    user = payload.get("created_by")

    event = WebSocketEvent(
        event_type=event_type, user=user, endpoint_id=endpoint_id, payload=payload
    )

    # Broadcast to all connected clients (we could refine this to send_to_user if needed)
    await connection_manager.broadcast(event)


def setup_websocket_bridge():
    """
    Subscribes the WebSocket bridge to relevant domain events.
    """
    event_dispatcher.subscribe("COMMAND_QUEUED", handle_command_event)
    event_dispatcher.subscribe("COMMAND_SENT", handle_command_event)
    event_dispatcher.subscribe("COMMAND_SUCCESS", handle_command_event)
    event_dispatcher.subscribe("COMMAND_FAILED", handle_command_event)
    logger.info("WebSocket bridge configured.")
