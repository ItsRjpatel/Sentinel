from pydantic import BaseModel, Field

class WindowsServiceInventoryData(BaseModel):
    """Pydantic validated DTO containing installed Windows Service details."""
    service_name: str = Field(..., max_length=255)
    display_name: str = Field(..., max_length=500)
    description: str = Field(..., max_length=1000)
    executable_path: str = Field(..., max_length=1000)
    current_state: str = Field(..., max_length=50)
    start_mode: str = Field(..., max_length=50)
    start_type: str = Field(..., max_length=50)
    service_type: str = Field(..., max_length=100)
    account_name: str = Field(..., max_length=255)
    process_id: int = Field(..., ge=0)
    binary_path: str = Field(..., max_length=1000)
    delayed_auto_start: bool
    error_control: str = Field(..., max_length=50)
    dependencies: str = Field(..., max_length=1000)
    dependent_services: str = Field(..., max_length=1000)
    can_stop: bool
    can_pause: bool
    can_shutdown: bool
    desktop_interaction: bool
    tag_id: int = Field(..., ge=0)
    is_critical: bool
    digital_signature_status: str = Field(..., max_length=255)
