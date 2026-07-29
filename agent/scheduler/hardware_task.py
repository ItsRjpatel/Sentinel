import logging
from agent.scheduler.scheduler import ScheduledTask
from agent.collectors.hardware.collector import HardwareCollector
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

logger = logging.getLogger(__name__)


class HardwareInventoryTask(ScheduledTask):
    """Periodically queries hardware specifications and uploads validated models to the Sentinel backend."""

    def __init__(
        self,
        interval_seconds: int,
        client: AgentHTTPClient,
        enrollment_manager: EnrollmentManager,
        collector: HardwareCollector
    ) -> None:
        super().__init__(interval_seconds)
        self.client = client
        self.enrollment_manager = enrollment_manager
        self.collector = collector

    async def execute(self) -> None:
        if not await self.enrollment_manager.is_enrolled():
            logger.warning("Agent check-in skipped. Registration credentials missing.")
            return

        logger.info("Initiating system hardware inventory query collection...")
        try:
            # Query Windows APIs (returns validated Pydantic DTO only)
            hardware_dto = self.collector.collect()

            # Upload details via communication layer client
            resp = await self.client.request(
                method="POST",
                path="inventory/hardware",
                json_data=hardware_dto.model_dump()
            )

            if resp.status_code == 200:
                logger.info("Hardware inventory details successfully reported to Sentinel backend.")
            else:
                logger.error(f"Hardware inventory upload rejected by server. Status code: {resp.status_code}")
        except Exception as e:
            logger.exception(f"Unexpected exception during hardware inventory upload loop: {e}")
