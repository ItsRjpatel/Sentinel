from typing import Optional
from pydantic import BaseModel, Field

class OperatingSystemInventoryData(BaseModel):
    """Pydantic validated DTO containing aggregated endpoint operating system details."""
    computer_name: str = Field(..., max_length=255)
    os_name: str = Field(..., max_length=255)
    edition: str = Field(..., max_length=255)
    version: str = Field(..., max_length=100)
    build_number: str = Field(..., max_length=100)
    display_version: str = Field(..., max_length=100)
    install_date: str = Field(..., max_length=100)
    last_boot_time: str = Field(..., max_length=100)
    uptime_seconds: int = Field(..., ge=0)
    system_architecture: str = Field(..., max_length=100)
    product_type: str = Field(..., max_length=100)
    registered_owner: str = Field(..., max_length=255)
    registered_organization: str = Field(..., max_length=255)
    windows_directory: str = Field(..., max_length=255)
    system_directory: str = Field(..., max_length=255)
    boot_device: str = Field(..., max_length=255)
    system_drive: str = Field(..., max_length=50)
    locale: str = Field(..., max_length=100)
    time_zone: str = Field(..., max_length=100)
    domain_workgroup: str = Field(..., max_length=255)
    activation_status: Optional[str] = Field(None, max_length=255)
