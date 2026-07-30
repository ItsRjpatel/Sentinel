from pydantic import BaseModel, Field

class WindowsUpdateInventoryData(BaseModel):
    """Pydantic validated DTO containing installed Windows Update details."""
    kb_number: str = Field(..., max_length=50)
    title: str = Field(..., max_length=500)
    description: str = Field(..., max_length=1000)
    category: str = Field(..., max_length=255)
    installed_by: str = Field(..., max_length=255)
    installed_on: str = Field(..., max_length=100)
    support_url: str = Field(..., max_length=500)
    update_id: str = Field(..., max_length=100)
    revision_number: int = Field(..., ge=0)
    operation_result: str = Field(..., max_length=100)
    severity: str = Field(..., max_length=50)
    source: str = Field(..., max_length=100)
    is_security_update: bool
    is_critical_update: bool
    is_feature_update: bool
    is_cumulative_update: bool
    requires_restart: bool
    is_hidden: bool
    is_downloaded: bool
    installed_state: str = Field(..., max_length=100)
