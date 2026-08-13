from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ScheduleBase(BaseModel):
    name: str
    job_type: str  # INVENTORY, COMMAND, POLICY_REFRESH, HEARTBEAT_CHECK, CLEANUP
    schedule_type: str = "RECURRING"  # RECURRING or ONE_TIME
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    status: Optional[str] = "ACTIVE"
    payload: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = 3


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class JobExecutionResponse(BaseModel):
    id: str
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ScheduleResponse(ScheduleBase):
    id: str
    last_run_at: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
