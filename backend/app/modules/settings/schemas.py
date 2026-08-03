from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any

class SettingItem(BaseModel):
    id: UUID4
    key: str
    category: str
    value: Dict[str, Any]
    description: Optional[str] = None

class SettingUpdateRequest(BaseModel):
    value: Dict[str, Any]
