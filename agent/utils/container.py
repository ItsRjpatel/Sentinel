from typing import Optional, Any
from agent.utils.storage import StorageProvider

class Container:
    """Dependency Injection Container for the Sentinel Windows Agent."""
    _instance: Optional['Container'] = None

    def __init__(self) -> None:
        self.config: Optional[Any] = None
        self.logger: Optional[Any] = None
        self.storage: Optional[StorageProvider] = None
        self.http_client: Optional[Any] = None
        self.scheduler: Optional[Any] = None
        self.enrollment_service: Optional[Any] = None
        self.heartbeat_service: Optional[Any] = None

    @classmethod
    def get_instance(cls) -> 'Container':
        if cls._instance is None:
            cls._instance = Container()
        return cls._instance
