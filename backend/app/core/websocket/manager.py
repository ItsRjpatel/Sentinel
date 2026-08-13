import logging
import asyncio
from typing import Dict, List, Set, Any
from fastapi import WebSocket
from app.core.websocket.schema import WebSocketEvent

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, websocket: WebSocket, username: str):
        self.websocket = websocket
        self.username = username
        self.active = True


class ConnectionManager:
    def __init__(self):
        # We store connections as a set for broadcast, and optionally by username/endpoint
        self.active_connections: Set[Connection] = set()

    async def connect(self, websocket: WebSocket, username: str) -> Connection:
        await websocket.accept()
        connection = Connection(websocket, username)
        self.active_connections.add(connection)
        logger.info(
            f"WebSocket client connected: {username}. Total connections: {len(self.active_connections)}"
        )
        return connection

    def disconnect(self, connection: Connection):
        if connection in self.active_connections:
            self.active_connections.remove(connection)
            logger.info(
                f"WebSocket client disconnected: {connection.username}. Total connections: {len(self.active_connections)}"
            )

    async def _send_safe(self, connection: Connection, message: dict):
        if not connection.active:
            return
        try:
            await connection.websocket.send_json(message)
        except Exception as e:
            logger.warning(
                f"Failed to send to {connection.username}, marking inactive: {e}"
            )
            connection.active = False
            self.disconnect(connection)

    async def broadcast(self, event: WebSocketEvent):
        message = event.model_dump()
        tasks = [
            self._send_safe(conn, message) for conn in list(self.active_connections)
        ]
        if tasks:
            await asyncio.gather(*tasks)

    async def send_to_user(self, username: str, event: WebSocketEvent):
        message = event.model_dump()
        tasks = [
            self._send_safe(conn, message)
            for conn in list(self.active_connections)
            if conn.username == username
        ]
        if tasks:
            await asyncio.gather(*tasks)

    async def send_to_endpoint(self, endpoint_id: str, event: WebSocketEvent):
        """
        Sends an event to clients associated with an endpoint.
        Usually this is broad if all admins can see all endpoints,
        but left here for specific filtering if needed.
        For now, this just broadcasts since the requirement doesn't specify strict tenant isolation for MVP.
        """
        # If we had tenant isolation, we'd check if conn.username has access to endpoint_id.
        # For this requirement, we broadcast or we can just send it if payload has endpoint_id.
        await self.broadcast(event)

    async def cleanup_dead_connections(self):
        """
        Periodically ping connections to clean up dead ones.
        """
        while True:
            await asyncio.sleep(30)
            logger.debug(
                f"Running WebSocket cleanup. Active connections: {len(self.active_connections)}"
            )
            for conn in list(self.active_connections):
                try:
                    await conn.websocket.send_json({"type": "ping"})
                except Exception:
                    logger.debug(f"Connection dead, removing: {conn.username}")
                    self.disconnect(conn)


connection_manager = ConnectionManager()
