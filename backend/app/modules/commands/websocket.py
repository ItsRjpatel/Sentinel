import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.websocket.manager import connection_manager
from app.core.websocket.auth import get_websocket_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/commands")
async def websocket_commands(
    websocket: WebSocket, username: str = Depends(get_websocket_user)
):
    """
    WebSocket endpoint for real-time command streaming.
    Authentication is done via query parameter 'token'.
    """
    connection = await connection_manager.connect(websocket, username)
    try:
        while True:
            # Wait for any message from client (e.g. ping)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected natively for user: {username}")
        connection_manager.disconnect(connection)
    except Exception as e:
        logger.error(f"WebSocket error for user {username}: {e}")
        connection_manager.disconnect(connection)
