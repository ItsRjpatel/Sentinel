import uuid
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.models import BaseModelMixin
from app.db.base import Base

class HardwareInventory(Base, BaseModelMixin):
    """Database model storing endpoint hardware specifications and configuration states."""
    __tablename__ = "hardware_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_version: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    bios_release_date: Mapped[str] = mapped_column(String(255), nullable=False)
    motherboard: Mapped[str] = mapped_column(String(255), nullable=False)
    cpu_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cpu_architecture: Mapped[str] = mapped_column(String(100), nullable=False)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False)
    cpu_logical_processors: Mapped[int] = mapped_column(Integer, nullable=False)
    installed_ram_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tpm_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    secure_boot_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_virtual: Mapped[bool] = mapped_column(Boolean, nullable=False)


class OperatingSystemInventory(Base, BaseModelMixin):
    """Database model storing endpoint operating system specifications and system state."""
    __tablename__ = "operating_system_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    computer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    os_name: Mapped[str] = mapped_column(String(255), nullable=False)
    edition: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    build_number: Mapped[str] = mapped_column(String(100), nullable=False)
    display_version: Mapped[str] = mapped_column(String(100), nullable=False)
    install_date: Mapped[str] = mapped_column(String(100), nullable=False)
    last_boot_time: Mapped[str] = mapped_column(String(100), nullable=False)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False)
    system_architecture: Mapped[str] = mapped_column(String(100), nullable=False)
    product_type: Mapped[str] = mapped_column(String(100), nullable=False)
    registered_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    registered_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    windows_directory: Mapped[str] = mapped_column(String(255), nullable=False)
    system_directory: Mapped[str] = mapped_column(String(255), nullable=False)
    boot_device: Mapped[str] = mapped_column(String(255), nullable=False)
    system_drive: Mapped[str] = mapped_column(String(50), nullable=False)
    locale: Mapped[str] = mapped_column(String(100), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(100), nullable=False)
    domain_workgroup: Mapped[str] = mapped_column(String(255), nullable=False)
    activation_status: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class NetworkAdapterInventory(Base, BaseModelMixin):
    """Database model storing endpoint network adapter details."""
    __tablename__ = "network_adapter_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    domain_workgroup: Mapped[str] = mapped_column(String(255), nullable=False)
    adapter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    adapter_description: Mapped[str] = mapped_column(String(255), nullable=False)
    interface_guid: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    ipv4: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ipv6: Mapped[str] = mapped_column(String(200), nullable=False)
    subnet_mask: Mapped[str] = mapped_column(String(100), nullable=False)
    gateway: Mapped[str] = mapped_column(String(100), nullable=False)
    dns_servers: Mapped[str] = mapped_column(String(500), nullable=False)
    dhcp_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    dhcp_server: Mapped[str] = mapped_column(String(100), nullable=False)
    lease_obtained: Mapped[str] = mapped_column(String(100), nullable=False)
    lease_expires: Mapped[str] = mapped_column(String(100), nullable=False)
    interface_speed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    interface_type: Mapped[str] = mapped_column(String(100), nullable=False)
    operational_status: Mapped[str] = mapped_column(String(50), nullable=False)
    is_physical: Mapped[bool] = mapped_column(Boolean, nullable=False)
    connection_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_vpn: Mapped[bool] = mapped_column(Boolean, nullable=False)


class PhysicalDiskInventory(Base, BaseModelMixin):
    """Database model storing endpoint physical disk details."""
    __tablename__ = "physical_disk_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    disk_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    firmware_version: Mapped[str] = mapped_column(String(100), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    bus_type: Mapped[str] = mapped_column(String(50), nullable=False)
    interface_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    partition_count: Mapped[int] = mapped_column(Integer, nullable=False)
    health_status: Mapped[str] = mapped_column(String(50), nullable=False)
    operational_status: Mapped[str] = mapped_column(String(50), nullable=False)
    is_boot_disk: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_system_disk: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_removable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_virtual: Mapped[bool] = mapped_column(Boolean, nullable=False)

    volumes: Mapped[list["LogicalVolumeInventory"]] = relationship(
        back_populates="disk", cascade="all, delete-orphan"
    )

class LogicalVolumeInventory(Base, BaseModelMixin):
    """Database model storing logical volume partitions linked to physical disks."""
    __tablename__ = "logical_volume_inventory"

    disk_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("physical_disk_inventory.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    disk: Mapped["PhysicalDiskInventory"] = relationship(back_populates="volumes")
    drive_letter: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    volume_name: Mapped[str] = mapped_column(String(255), nullable=False)
    volume_guid: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    file_system: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    free_space_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    used_space_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    compression_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    bitlocker_status: Mapped[str] = mapped_column(String(100), nullable=False)
    volume_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_boot_volume: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_system_volume: Mapped[bool] = mapped_column(Boolean, nullable=False)
    shadow_copy_support: Mapped[bool] = mapped_column(Boolean, nullable=False)


class SoftwareInventory(Base, BaseModelMixin):
    """Database model storing endpoint installed software application details."""
    __tablename__ = "software_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    application_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    publisher: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    install_date: Mapped[str] = mapped_column(String(50), nullable=False)
    install_location: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_size_kb: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uninstall_string: Mapped[str] = mapped_column(String(500), nullable=False)
    install_source: Mapped[str] = mapped_column(String(500), nullable=False)
    architecture: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    product_code: Mapped[str] = mapped_column(String(100), nullable=False)
    system_component: Mapped[bool] = mapped_column(Boolean, nullable=False)
    windows_installer: Mapped[bool] = mapped_column(Boolean, nullable=False)
    url_info: Mapped[str] = mapped_column(String(500), nullable=False)
    help_link: Mapped[str] = mapped_column(String(500), nullable=False)
    modify_path: Mapped[str] = mapped_column(String(500), nullable=False)
    install_scope: Mapped[str] = mapped_column(String(50), nullable=False)
    registry_key: Mapped[str] = mapped_column(String(500), nullable=False)


class WindowsUpdateInventory(Base, BaseModelMixin):
    """Database model storing endpoint Windows Update history and installed patches."""
    __tablename__ = "windows_update_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    kb_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    installed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    installed_on: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    support_url: Mapped[str] = mapped_column(String(500), nullable=False)
    update_id: Mapped[str] = mapped_column(String(100), nullable=False)
    revision_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operation_result: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    is_security_update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_critical_update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_feature_update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_cumulative_update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    requires_restart: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_downloaded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    installed_state: Mapped[str] = mapped_column(String(100), nullable=False)


class WindowsServiceInventory(Base, BaseModelMixin):
    """Database model storing endpoint Windows Services information."""
    __tablename__ = "windows_service_inventory"

    endpoint_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("endpoints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    service_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    executable_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    current_state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    start_mode: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    start_type: Mapped[str] = mapped_column(String(50), nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    process_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    binary_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    delayed_auto_start: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_control: Mapped[str] = mapped_column(String(50), nullable=False)
    dependencies: Mapped[str] = mapped_column(String(1000), nullable=False)
    dependent_services: Mapped[str] = mapped_column(String(1000), nullable=False)
    can_stop: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_pause: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_shutdown: Mapped[bool] = mapped_column(Boolean, nullable=False)
    desktop_interaction: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tag_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False)
    digital_signature_status: Mapped[str] = mapped_column(String(255), nullable=False)
