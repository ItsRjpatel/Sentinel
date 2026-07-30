import logging
from agent.scheduler.scheduler import ScheduledTask
from agent.collectors.software.collector import SoftwareCollector
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

logger = logging.getLogger(__name__)


class SoftwareInventoryTask(ScheduledTask):
    """Periodically queries local Windows Registry for installed software and posts validated DTOs to Sentinel backend."""

    def __init__(
        self,
        interval_seconds: int,
        client: AgentHTTPClient,
        enrollment_manager: EnrollmentManager,
        collector: SoftwareCollector
    ) -> None:
        super().__init__(interval_seconds)
        self.client = client
        self.enrollment_manager = enrollment_manager
        self.collector = collector

    async def execute(self) -> None:
        if not await self.enrollment_manager.is_enrolled():
            logger.warning("Agent check-in skipped. Registration credentials missing.")
            return

        logger.info("Initiating installed software inventory query loop...")

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
            # Discover installed software
            software_dtos = await asyncio.to_thread(run_collector)

            # ===== DEBUG LOGS =====
            logger.info(f"Collected {len(software_dtos)} software entries.")

            if software_dtos:
                logger.info(
                    f"First software: {software_dtos[0].application_name} "
                    f"| Version: {software_dtos[0].version}"
                )
            else:
                logger.warning("Software collector returned an empty list.")
            # ======================

            # Dispatch payload via HTTP transport client
            resp = await self.client.request(
                method="POST",
                path="inventory/software",
                json_data=[item.model_dump() for item in software_dtos]
            )

            if resp.status_code == 200:
                logger.info(
                    f"Software inventory successfully reported to Sentinel backend. "
                    f"Total entries: {len(software_dtos)}"
                )
            else:
                logger.error(
                    f"Software inventory upload rejected by server. "
                    f"Status code: {resp.status_code}"
                )

        except Exception as e:
            logger.exception(
                f"Unexpected exception during software inventory upload loop: {e}"
            )