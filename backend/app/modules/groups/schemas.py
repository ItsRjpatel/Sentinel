from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    group_type: str = "STATIC"  # STATIC or DYNAMIC
    criteria: Optional[Dict[str, Any]] = None
    site: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None


class GroupCreate(GroupBase):
    endpoint_ids: Optional[List[str]] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    site: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None


class GroupStats(BaseModel):
    endpoint_count: int = 0
    online_count: int = 0
    offline_count: int = 0
    compliance_percent: float = 100.0
    health_percent: float = 100.0


class GroupResponse(GroupBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    stats: Optional[GroupStats] = None

    class Config:
        from_attributes = True


class GroupBulkAssignRequest(BaseModel):
    group_ids: List[str]
    endpoint_ids: List[str]
