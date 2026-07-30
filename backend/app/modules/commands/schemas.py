from pydantic import BaseModel, Field, UUID4
from typing import Optional, Any, Dict, List
from datetime import datetime
from app.modules.commands.enums import CommandStatus, CommandType

class CommandCreate(BaseModel):
    endpoint_id: UUID4
    command_type: CommandType
    payload: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    expires_in_seconds: Optional[int] = Field(default=3600, description="Seconds until command expires")

class CommandResponse(BaseModel):
    id: UUID4
    endpoint_id: UUID4
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

    class Config:
        from_attributes = True

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
