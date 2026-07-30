from typing import List, Optional
from pydantic import BaseModel, Field

class LogicalVolumeInventoryData(BaseModel):
    """Pydantic validated DTO containing logical volume partition properties."""
    drive_letter: str = Field(..., max_length=10)
    volume_name: str = Field(..., max_length=255)
    volume_guid: str = Field(..., max_length=100)
    file_system: str = Field(..., max_length=50)
    label: str = Field(..., max_length=255)
    capacity_bytes: int = Field(..., ge=0)
    free_space_bytes: int = Field(..., ge=0)
    used_space_bytes: int = Field(..., ge=0)
    compression_enabled: bool
    bitlocker_status: str = Field(..., max_length=100)
    volume_type: str = Field(..., max_length=100)
    is_boot_volume: bool
    is_system_volume: bool
    shadow_copy_support: bool


class PhysicalDiskInventoryData(BaseModel):
    """Pydantic validated DTO containing physical disk drive properties."""
    disk_number: int = Field(..., ge=0)
    model: str = Field(..., max_length=255)
    manufacturer: str = Field(..., max_length=255)
    serial_number: str = Field(..., max_length=255)
    firmware_version: str = Field(..., max_length=100)
    media_type: str = Field(..., max_length=50)
    bus_type: str = Field(..., max_length=50)
    interface_type: str = Field(..., max_length=50)
    size_bytes: int = Field(..., ge=0)
    partition_count: int = Field(..., ge=0)
    health_status: str = Field(..., max_length=50)
    operational_status: str = Field(..., max_length=50)
    is_boot_disk: bool
    is_system_disk: bool
    is_removable: bool
    is_virtual: bool
    volumes: List[LogicalVolumeInventoryData] = []
