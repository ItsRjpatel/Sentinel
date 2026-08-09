from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    severity: str = "INFO" # INFO, WARNING, ERROR, CRITICAL
    category: str = "SYSTEM" # SYSTEM, SECURITY, COMMAND, COMPLIANCE
    link: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: Optional[str] = None

from uuid import UUID

class NotificationResponse(NotificationBase):
    id: UUID
    is_read: bool
    user_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationPreferenceSchema(BaseModel):
    email_enabled: bool = True
    email_address: Optional[str] = None
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    teams_enabled: bool = False
    teams_webhook_url: Optional[str] = None
    min_severity: str = "INFO"

    class Config:
        from_attributes = True
