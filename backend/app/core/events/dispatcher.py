import logging
import asyncio
from typing import Callable, Awaitable, Any, Dict, List

logger = logging.getLogger(__name__)

EventHandler = Callable[[str, Any], Awaitable[None]]


class EventDispatcher:
    """
    A simple async event bus for decoupled in-process communication.
    The Service layer publishes events here, without knowing about WebSockets.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, payload: Any) -> None:
        """
        Publish an event asynchronously.
        Does not block the caller.
        """
        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            return

        async def _dispatch():
            for handler in handlers:
                try:
                    await handler(event_type, payload)
                except Exception as e:
                    logger.error(f"Error handling event {event_type}: {e}")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_dispatch())
        except RuntimeError:
            asyncio.run(_dispatch())


# Global singleton
event_dispatcher = EventDispatcher()
