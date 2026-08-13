from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertNoteItem(BaseModel):
    author: str
    timestamp: str
    content: str


class AlertResponse(BaseModel):
    id: UUID4
    title: str
    severity: str
    category: str
    description: str
    endpoint_id: Optional[UUID4] = None
    endpoint_name: str
    status: str
    assigned_analyst: Optional[str] = None
    resolution_notes: Optional[str] = None
    notes: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaginatedAlertsResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    size: int


class AlertSummaryData(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    informational: int
    active: int
    acknowledged: int
    resolved: int


class AlertAssignRequest(BaseModel):
    analyst: str


class AlertNoteRequest(BaseModel):
    note: str


class AlertResolveRequest(BaseModel):
    resolution_notes: Optional[str] = None
