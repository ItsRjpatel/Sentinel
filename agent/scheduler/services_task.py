import logging
from agent.scheduler.scheduler import ScheduledTask
from agent.collectors.services.collector import WindowsServiceCollector
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

logger = logging.getLogger(__name__)


class WindowsServiceInventoryTask(ScheduledTask):
    """Periodically queries local WMI for installed Windows Services and posts validated DTOs to Sentinel backend."""

    def __init__(
        self,
        interval_seconds: int,
        client: AgentHTTPClient,
        enrollment_manager: EnrollmentManager,
        collector: WindowsServiceCollector
    ) -> None:
        super().__init__(interval_seconds)
        self.client = client
        self.enrollment_manager = enrollment_manager
        self.collector = collector

    async def execute(self) -> None:
        if not await self.enrollment_manager.is_enrolled():
            logger.warning("Agent check-in skipped. Registration credentials missing.")
            return

        logger.info("Initiating Windows Service inventory query loop...")
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
            # Discover installed Windows Services
            service_dtos = await asyncio.to_thread(run_collector)

            # Dispatch payload via HTTP transport client
            resp = await self.client.request(
                method="POST",
                path="inventory/services",
                json_data=[item.model_dump() for item in service_dtos]
            )

            if resp.status_code == 200:
                logger.info(f"Windows Service inventory successfully reported to Sentinel backend. Total entries: {len(service_dtos)}")
            else:
                logger.error(f"Windows Service inventory upload rejected by server. Status code: {resp.status_code}")
        except Exception as e:
            logger.exception(f"Unexpected exception during Windows Service inventory upload loop: {e}")
