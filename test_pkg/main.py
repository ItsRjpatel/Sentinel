
import asyncio
_stop_event = None
def start():
    global _stop_event
    _stop_event = asyncio.Event()
