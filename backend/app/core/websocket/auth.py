from fastapi import WebSocket, WebSocketException, status
from app.core.security import verify_access_token

async def get_websocket_user(websocket: WebSocket) -> str:
    """
    Reusable WebSocketAuth helper.
    Extracts the JWT from the 'token' query parameter and verifies it.
    Returns the username/subject from the token.
    Raises WebSocketException if missing or invalid.
    """
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token query parameter.")
        
    try:
        payload = verify_access_token(token)
        user = payload.get("sub")
        if not user:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing subject identifier.")
        return user
    except Exception as e:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=f"Invalid token: {e}")
