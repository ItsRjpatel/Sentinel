import logging
from agent.scheduler.scheduler import ScheduledTask
from agent.collectors.storage.collector import StorageCollector
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

logger = logging.getLogger(__name__)


class DiskInventoryTask(ScheduledTask):
    """Periodically queries local physical disk and logical volume details and uploads validated models."""

    def __init__(self, interval_seconds: int, client: AgentHTTPClient, enrollment_manager: EnrollmentManager, collector: StorageCollector) -> None:
        super().__init__(interval_seconds)
        self.client = client
        self.enrollment_manager = enrollment_manager
        self.collector = collector

    async def execute(self) -> None:
        if not await self.enrollment_manager.is_enrolled():
            logger.warning("Agent check-in skipped. Registration credentials missing.")
            return

        logger.info("Initiating storage adapter configuration queries...")
        import asyncio
        def run_collector():
            import os
            if os.name == "nt":
                import pythoncom
                pythoncom.CoInitialize()
            try:
                return self.collector.collect()
            finally:
                if os.name == "nt":
                    import pythoncom
                    pythoncom.CoUninitialize()

        try:
            # Discover installed disks and logical partitions
            disks_dto = await asyncio.to_thread(run_collector)

            # Upload details via communication layer client
            resp = await self.client.request(
                method="POST",
                path="inventory/storage",
                json_data=[d.model_dump() for d in disks_dto]
            )

            if resp.status_code == 200:
                logger.info("Storage inventory details successfully reported to Sentinel backend.")
            else:
                logger.error(f"Storage inventory upload rejected by server. Status code: {resp.status_code}")
        except Exception as e:
            logger.exception(f"Unexpected exception during storage inventory upload loop: {e}")
