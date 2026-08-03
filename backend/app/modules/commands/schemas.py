from pydantic import BaseModel, Field, UUID4, field_validator
from typing import Optional, Any, Dict, List
from datetime import datetime
from app.modules.commands.enums import CommandStatus, CommandType

class CommandCreate(BaseModel):
    endpoint_id: UUID4
    command_type: CommandType
    payload: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    expires_in_seconds: Optional[int] = Field(default=3600, description="Seconds until command expires")
    scheduled_at: Optional[datetime] = None
    recurring: Optional[str] = None
    timezone: Optional[str] = None

class BulkCommandCreate(BaseModel):
    endpoint_ids: List[UUID4]
    command_type: CommandType
    payload: Optional[Dict[str, Any]] = None
    expires_in_seconds: Optional[int] = Field(default=3600)
    scheduled_at: Optional[datetime] = None
    timezone: Optional[str] = None

class BulkCommandResponse(BaseModel):
    queued_count: int
    command_ids: List[UUID4]

class CommandResponse(BaseModel):
    id: UUID4
    endpoint_id: UUID4
    endpoint_hostname: Optional[str] = None
    endpoint_type: Optional[str] = None
    command_type: CommandType
    status: CommandStatus
    payload: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int
    expires_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    recurring: Optional[str] = None
    timezone: Optional[str] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper == "COMPLETED":
                return CommandStatus.SUCCESS
            if hasattr(CommandStatus, v_upper):
                return CommandStatus[v_upper]
            for member in CommandStatus:
                if member.value == v_upper:
                    return member
        return v

    @field_validator("command_type", mode="before")
    @classmethod
    def normalize_command_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.upper()
            if hasattr(CommandType, v_upper):
                return CommandType[v_upper]
            for member in CommandType:
                if member.value == v_upper:
                    return member
        return v

    class Config:
        from_attributes = True

class CommandSummary(BaseModel):
    pending: int
    running: int
    success: int
    failed: int
    timed_out: int
    cancelled: int
    scheduled: int
    total: int

class PaginatedCommandResponse(BaseModel):
    items: List[CommandResponse]
    total: int
    page: int
    size: int

class CommandResultRequest(BaseModel):
    success: bool
    duration_ms: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CommandResult(BaseModel):
    status: CommandStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class CommandStatusUpdate(BaseModel):
    status: CommandStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class CommandQueueResponse(BaseModel):
    command_id: UUID4
    status: CommandStatus
    message: str
