import time
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

class AbstractTask(ABC):
    """Abstract base class representing a scheduled task in the system."""

    @abstractmethod
    async def run(self) -> None:
        """Evaluate task schedules and trigger executions."""
        pass


class ScheduledTask(AbstractTask):
    """A task that executes on a defined periodic interval in seconds."""

    def __init__(self, interval_seconds: int) -> None:
        self.interval = interval_seconds
        self.last_run = 0.0

    async def run(self) -> None:
        current_time = time.monotonic()
        if current_time - self.last_run >= self.interval:
            # Update last run before executing to prevent overlaps on long executions
            self.last_run = current_time
            try:
                await self.execute()
            except Exception as e:
                logger.error(f"Error executing task {self.__class__.__name__}: {e}")

    @abstractmethod
    async def execute(self) -> None:
        """The actual task execution logic."""
        pass


class Scheduler:
    """Async task runner running registered tasks on background loops."""

    def __init__(self) -> None:
        self.tasks: List[AbstractTask] = []
        self._running = False
        self._runner_task: Optional[asyncio.Task] = None

    def register_task(self, task: AbstractTask) -> None:
        """Add a task to the registry scheduler."""
        self.tasks.append(task)

    async def start(self) -> None:
        """Initiate background scheduler executions."""
        if self._running:
            return
        self._running = True
        self._runner_task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler started background execution loops.")

    async def stop(self) -> None:
        """Cancel and clean up all running scheduler task loops."""
        if not self._running:
            return
        self._running = False
        if self._runner_task:
            self._runner_task.cancel()
            try:
                await self._runner_task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped background loops.")

    async def _run_loop(self) -> None:
        while self._running:
            for task in self.tasks:
                # Runs concurrently if tasks are async
                await task.run()
            await asyncio.sleep(0.5)
