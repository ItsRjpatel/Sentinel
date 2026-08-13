from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime


class AuditLogItem(BaseModel):
    id: UUID4
    timestamp: datetime
    actor: str
    actor_type: str
    endpoint_id: Optional[UUID4] = None
    endpoint_hostname: Optional[str] = None
    action: str
    module: str
    resource: Optional[str] = None
    severity: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class PaginatedAuditResponse(BaseModel):
    items: List[AuditLogItem]
    total: int
    page: int
    size: int


class AuditSummary(BaseModel):
    total: int
    critical: int
    warning: int
    information: int
    success: int
    failed: int
    today: int
