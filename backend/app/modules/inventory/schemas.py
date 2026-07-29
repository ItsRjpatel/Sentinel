import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class HardwareInventoryBase(BaseModel):
    manufacturer: str = Field(..., max_length=255)
    model: str = Field(..., max_length=255)
    serial_number: str = Field(..., max_length=255)
    bios_version: str = Field(..., max_length=255)
    bios_manufacturer: str = Field(..., max_length=255)
    bios_release_date: str = Field(..., max_length=255)
    motherboard: str = Field(..., max_length=255)
    cpu_name: str = Field(..., max_length=255)
    cpu_architecture: str = Field(..., max_length=100)
    cpu_cores: int = Field(..., ge=1)
    cpu_logical_processors: int = Field(..., ge=1)
    installed_ram_bytes: int = Field(..., ge=0)
    tpm_version: Optional[str] = Field(None, max_length=50)
    secure_boot_enabled: bool
    is_virtual: bool

class HardwareInventoryCreate(HardwareInventoryBase):
    pass

class HardwareInventoryResponse(HardwareInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
