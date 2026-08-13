import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.core.websocket.schema import WebSocketEvent
from app.core.events.dispatcher import event_dispatcher
from app.core.websocket.manager import connection_manager, Connection
from app.core.websocket.bridge import setup_websocket_bridge


@pytest.mark.asyncio
async def test_websocket_manager_and_dispatcher():
    # Setup mock websocket
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_json = AsyncMock()

    # Test connect
    connection = await connection_manager.connect(mock_ws, "testuser")
    assert connection in connection_manager.active_connections
    assert connection.username == "testuser"
    mock_ws.accept.assert_called_once()

    # Test send_to_user
    event = WebSocketEvent(event_type="TEST", user="testuser", payload={"data": 123})
    await connection_manager.send_to_user("testuser", event)
    mock_ws.send_json.assert_called_once_with(event.model_dump())

    mock_ws.send_json.reset_mock()

    # Test Event Bridge
    setup_websocket_bridge()

    event_payload = {
        "endpoint_id": "ep1",
        "command_type": "PING",
        "status": "QUEUED",
        "created_by": "testuser",
        "payload": {},
    }

    event_dispatcher.publish("COMMAND_QUEUED", event_payload)

    # Let event loop tick for async dispatch
    await asyncio.sleep(0.1)

    mock_ws.send_json.assert_called_once()
    call_args = mock_ws.send_json.call_args[0][0]
    assert call_args["event_type"] == "COMMAND_QUEUED"
    assert call_args["user"] == "testuser"

    # Test disconnect
    connection_manager.disconnect(connection)
    assert connection not in connection_manager.active_connections
