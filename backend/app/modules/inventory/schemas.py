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


class OperatingSystemInventoryBase(BaseModel):
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


class OperatingSystemInventoryCreate(OperatingSystemInventoryBase):
    pass


class OperatingSystemInventoryResponse(OperatingSystemInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NetworkAdapterInventoryBase(BaseModel):
    hostname: str = Field(..., max_length=255)
    domain_workgroup: str = Field(..., max_length=255)
    adapter_name: str = Field(..., max_length=255)
    adapter_description: str = Field(..., max_length=255)
    interface_guid: str = Field(..., max_length=100)
    mac_address: Optional[str] = Field(None, max_length=100)
    ipv4: str = Field(..., max_length=100)
    ipv6: str = Field(..., max_length=200)
    subnet_mask: str = Field(..., max_length=100)
    gateway: str = Field(..., max_length=100)
    dns_servers: str = Field(..., max_length=500)
    dhcp_enabled: bool
    dhcp_server: str = Field(..., max_length=100)
    lease_obtained: str = Field(..., max_length=100)
    lease_expires: str = Field(..., max_length=100)
    interface_speed: int = Field(..., ge=0)
    interface_type: str = Field(..., max_length=100)
    operational_status: str = Field(..., max_length=50)
    is_physical: bool
    connection_type: str = Field(..., max_length=50)
    is_vpn: bool


class NetworkAdapterInventoryCreate(NetworkAdapterInventoryBase):
    pass


class NetworkAdapterInventoryResponse(NetworkAdapterInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogicalVolumeInventoryBase(BaseModel):
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


class LogicalVolumeInventoryCreate(LogicalVolumeInventoryBase):
    pass


class LogicalVolumeInventoryResponse(LogicalVolumeInventoryBase):
    id: uuid.UUID
    disk_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PhysicalDiskInventoryBase(BaseModel):
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


class PhysicalDiskInventoryCreate(PhysicalDiskInventoryBase):
    volumes: list[LogicalVolumeInventoryCreate] = []


class PhysicalDiskInventoryResponse(PhysicalDiskInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    volumes: list[LogicalVolumeInventoryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SoftwareInventoryBase(BaseModel):
    application_name: str = Field(..., max_length=255)
    publisher: str = Field(..., max_length=255)
    version: str = Field(..., max_length=100)
    install_date: str = Field(..., max_length=50)
    install_location: str = Field(..., max_length=500)
    estimated_size_kb: int = Field(..., ge=0)
    uninstall_string: str = Field(..., max_length=500)
    install_source: str = Field(..., max_length=500)
    architecture: str = Field(..., max_length=50)
    language: str = Field(..., max_length=50)
    product_code: str = Field(..., max_length=100)
    system_component: bool
    windows_installer: bool
    url_info: str = Field(..., max_length=500)
    help_link: str = Field(..., max_length=500)
    modify_path: str = Field(..., max_length=500)
    install_scope: str = Field(..., max_length=50)
    registry_key: str = Field(..., max_length=500)


class SoftwareInventoryCreate(SoftwareInventoryBase):
    pass


class SoftwareInventoryResponse(SoftwareInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WindowsUpdateInventoryBase(BaseModel):
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


class WindowsUpdateInventoryCreate(WindowsUpdateInventoryBase):
    pass


class WindowsUpdateInventoryResponse(WindowsUpdateInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WindowsServiceInventoryBase(BaseModel):
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


class WindowsServiceInventoryCreate(WindowsServiceInventoryBase):
    pass


class WindowsServiceInventoryResponse(WindowsServiceInventoryBase):
    id: uuid.UUID
    endpoint_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
