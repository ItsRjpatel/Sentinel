from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.schedules.schemas import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    JobExecutionResponse,
)
from app.modules.schedules.service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=List[ScheduleResponse])
async def list_scheduled_jobs(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    return await service.list_jobs(status)


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_job(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    return await service.create_job(data, current_user.username)


@router.get("/{job_id}", response_model=ScheduleResponse)
async def get_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return job


@router.put("/{job_id}", response_model=ScheduleResponse)
async def update_scheduled_job(
    job_id: str,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    updated = await service.update_job(job_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return updated


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    success = await service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scheduled job not found")


@router.post("/{job_id}/run-now", response_model=JobExecutionResponse)
async def run_scheduled_job_now(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    history = await service.execute_job_now(job_id)
    if not history:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return history


@router.get("/{job_id}/history", response_model=List[JobExecutionResponse])
async def get_job_history(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ScheduleService(db)
    return await service.get_history(job_id)
