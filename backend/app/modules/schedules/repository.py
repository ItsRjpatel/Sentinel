from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.modules.schedules.models import ScheduledJob, JobExecutionHistory

class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: ScheduledJob) -> ScheduledJob:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> Optional[ScheduledJob]:
        result = await self.session.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        return result.scalars().first()

    async def list_jobs(self, status: Optional[str] = None) -> List[ScheduledJob]:
        query = select(ScheduledJob)
        if status:
            query = query.where(ScheduledJob.status == status)
        result = await self.session.execute(query.order_by(ScheduledJob.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, job: ScheduledJob) -> ScheduledJob:
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def delete(self, job_id: str) -> bool:
        job = await self.get_by_id(job_id)
        if not job:
            return False
        await self.session.delete(job)
        await self.session.commit()
        return True

    async def record_execution(self, history: JobExecutionHistory) -> JobExecutionHistory:
        self.session.add(history)
        await self.session.commit()
        await self.session.refresh(history)
        return history

    async def get_execution_history(self, job_id: str) -> List[JobExecutionHistory]:
        result = await self.session.execute(
            select(JobExecutionHistory).where(JobExecutionHistory.job_id == job_id).order_by(JobExecutionHistory.started_at.desc())
        )
        return list(result.scalars().all())
