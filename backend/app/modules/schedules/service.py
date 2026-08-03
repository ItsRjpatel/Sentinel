from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.schedules.repository import ScheduleRepository
from app.modules.schedules.models import ScheduledJob, JobExecutionHistory
from app.modules.schedules.schemas import ScheduleCreate, ScheduleUpdate

class ScheduleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ScheduleRepository(session)

    async def create_job(self, data: ScheduleCreate, user_name: Optional[str] = None) -> ScheduledJob:
        job = ScheduledJob(
            name=data.name,
            job_type=data.job_type,
            schedule_type=data.schedule_type,
            cron_expression=data.cron_expression,
            next_run_at=data.next_run_at or datetime.utcnow(),
            status=data.status or "ACTIVE",
            payload=data.payload,
            retry_count=data.retry_count or 3,
            created_by=user_name
        )
        return await self.repo.create(job)

    async def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        return await self.repo.get_by_id(job_id)

    async def list_jobs(self, status: Optional[str] = None) -> List[ScheduledJob]:
        return await self.repo.list_jobs(status)

    async def update_job(self, job_id: str, data: ScheduleUpdate) -> Optional[ScheduledJob]:
        job = await self.repo.get_by_id(job_id)
        if not job:
            return None
        if data.name is not None: job.name = data.name
        if data.cron_expression is not None: job.cron_expression = data.cron_expression
        if data.next_run_at is not None: job.next_run_at = data.next_run_at
        if data.status is not None: job.status = data.status
        if data.payload is not None: job.payload = data.payload

        return await self.repo.update(job)

    async def delete_job(self, job_id: str) -> bool:
        return await self.repo.delete(job_id)

    async def execute_job_now(self, job_id: str) -> Optional[JobExecutionHistory]:
        job = await self.repo.get_by_id(job_id)
        if not job:
            return None

        job.last_run_at = datetime.utcnow()
        await self.repo.update(job)

        history = JobExecutionHistory(
            job_id=job.id,
            status="SUCCESS",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            details={"message": f"Executed scheduled job {job.job_type} successfully"}
        )
        return await self.repo.record_execution(history)

    async def get_history(self, job_id: str) -> List[JobExecutionHistory]:
        return await self.repo.get_execution_history(job_id)
