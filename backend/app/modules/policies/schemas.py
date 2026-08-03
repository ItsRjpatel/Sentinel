from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str # Defender, Firewall, BitLocker, USB, Password, WindowsUpdate, RDP, Power
    settings: Dict[str, Any]
    status: Optional[str] = "ACTIVE"

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    change_summary: Optional[str] = None

class PolicyVersionResponse(BaseModel):
    id: str
    policy_id: str
    version: int
    settings: Dict[str, Any]
    change_summary: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PolicyResponse(PolicyBase):
    id: str
    version: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PolicyAssignRequest(BaseModel):
    target_type: str # ENDPOINT or GROUP
    target_ids: List[str]

class PolicyConflictInfo(BaseModel):
    has_conflict: bool
    conflicting_policies: List[str] = []
    conflict_details: Optional[str] = None
