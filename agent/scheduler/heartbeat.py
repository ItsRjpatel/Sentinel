import logging
import httpx
from datetime import datetime, timezone
from agent.scheduler.scheduler import ScheduledTask
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager
from agent.utils.storage import StorageProvider

logger = logging.getLogger(__name__)

class HeartbeatTask(ScheduledTask):
    """Periodic task that runs check-ins, handles offline modes, and triggers re-enrollment on auth failures."""

    def __init__(
        self,
        interval_seconds: int,
        client: AgentHTTPClient,
        storage: StorageProvider,
        enrollment_manager: EnrollmentManager,
        config_version: str = "1.0.0"
    ) -> None:
        super().__init__(interval_seconds)
        self.client = client
        self.storage = storage
        self.enrollment_manager = enrollment_manager
        self.config_version = config_version
        self.is_online = True

    async def execute(self) -> None:
        if not await self.enrollment_manager.is_enrolled():
            logger.warning("Agent not enrolled. Heartbeat execution skipped.")
            return

        import psutil
        import socket
        from agent.collectors.security.collector import SecurityCollector
        
        security_collector = SecurityCollector()
        security_data = security_collector.collect().model_dump()
        
        # Gather active non-loopback IPs
        try:
            ips = socket.gethostbyname_ex(socket.gethostname())[2]
            ips = [ip for ip in ips if ip not in ("127.0.0.1", "0.0.0.0")]
        except Exception:
            ips = []
        
        payload = {
            "status": "healthy",
            "current_config_version": self.config_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "cpu_usage_percent": psutil.cpu_percent(interval=None),
                "memory_usage_percent": psutil.virtual_memory().percent,
                "memory_free_bytes": psutil.virtual_memory().available,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "disk_free_bytes": psutil.disk_usage('/').free
            },
            "security": security_data,
            "ip_addresses": ips
        }

        try:
            resp = await self.client.request(
                method="POST",
                path="endpoints/heartbeat",
                json_data=payload
            )

            if resp.status_code == 200:
                if not self.is_online:
                    logger.info("Agent network connection restored. Transitioning state: OFFLINE -> ONLINE.")
                    self.is_online = True
                    await self._drain_offline_queue()
            elif resp.status_code in (401, 403):
                logger.error("Authentication check failed. Transitioning state: AUTHENTICATION_FAILED -> RE_ENROLLMENT.")
                # Clear tokens and identity configuration to trigger a fresh registration handshake
                await self.storage.delete("tokens")
                await self.storage.delete("identity")
                await self.enrollment_manager.enroll()
            else:
                raise httpx.HTTPStatusError(
                    f"Unexpected heartbeat response status {resp.status_code}",
                    request=resp.request,
                    response=resp
                )

        except Exception as e:
            if self.is_online:
                logger.warning(f"Connection lost during heartbeat: {e}. Transitioning state: ONLINE -> OFFLINE.")
                self.is_online = False
            
            # Persist offline telemetry metrics through storage provider abstraction
            await self._enqueue_offline_telemetry(payload)

    async def _enqueue_offline_telemetry(self, payload: dict) -> None:
        """Saves telemetry payload to the local offline cache file via the StorageProvider."""
        queue = await self.storage.read("telemetry_queue") or []
        # Apply FIFO cap of 50 entries
        if len(queue) >= 50:
            queue.pop(0)
        queue.append(payload)
        await self.storage.write("telemetry_queue", queue)
        logger.info(f"Heartbeat telemetry saved to local offline cache. Queue size: {len(queue)}")

    async def _drain_offline_queue(self) -> None:
        """Drains local queued metrics in chronological order when agent reconnects."""
        queue = await self.storage.read("telemetry_queue") or []
        if not queue:
            return

        logger.info(f"Reconnected. Draining {len(queue)} local telemetry logs from storage...")
        
        for item in list(queue):
            try:
                resp = await self.client.request(
                    method="POST",
                    path="endpoints/heartbeat",
                    json_data=item
                )
                if resp.status_code == 200:
                    queue.remove(item)
                    await self.storage.write("telemetry_queue", queue)
                else:
                    break
            except Exception:
                # Connection dropped mid-drain suspend execution
                break
