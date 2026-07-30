import logging
from typing import Any, Dict
from agent.collectors.storage.models import PhysicalDiskInventoryData, LogicalVolumeInventoryData

logger = logging.getLogger(__name__)

def map_media_type(raw_type: Any) -> str:
    """Maps MSFT_Disk MediaType to readable strings."""
    mapping = {
        0: "Unspecified",
        3: "HDD",
        4: "SSD",
        5: "SCM"
    }
    if isinstance(raw_type, int) and raw_type in mapping:
        return mapping[raw_type]
    return "Unknown"


def map_bus_type(raw_type: Any) -> str:
    """Maps MSFT_Disk BusType to readable strings."""
    mapping = {
        0: "Unknown",
        1: "SCSI",
        2: "ATAPI",
        3: "ATA",
        4: "1394",
        5: "SSA",
        6: "Fibre Channel",
        7: "USB",
        8: "RAID",
        9: "iSCSI",
        10: "SAS",
        11: "SATA",
        12: "SD",
        13: "MMC",
        14: "Virtual",
        15: "File Backed Virtual",
        16: "Storage Spaces",
        17: "NVMe"
    }
    if isinstance(raw_type, int) and raw_type in mapping:
        return mapping[raw_type]
    return str(raw_type) if raw_type else "Unknown"

def clean_str(val: Any, default: str = "Unknown") -> str:
    if val is None:
        return default
    s = str(val).strip()
    return s if s else default

def map_bitlocker_status(status_code: Any) -> str:
    """Maps Win32_EncryptableVolume ProtectionStatus."""
    # 0 = Unprotected, 1 = Protected, 2 = Unknown
    if status_code == 1:
        return "Encrypted"
    elif status_code == 0:
        return "Unencrypted"
    return "Unknown"


def map_raw_logical_volume(raw: Dict[str, Any]) -> LogicalVolumeInventoryData:
    capacity = int(raw.get("capacity_bytes") or 0)
    free = int(raw.get("free_space_bytes") or 0)
    used = capacity - free
    if used < 0:
        used = 0

    return LogicalVolumeInventoryData(
        drive_letter=clean_str(raw.get("drive_letter")),
        volume_name=clean_str(raw.get("volume_name")),
        volume_guid=clean_str(raw.get("volume_guid")),
        file_system=clean_str(raw.get("file_system")),
        label=clean_str(raw.get("label")),
        capacity_bytes=capacity,
        free_space_bytes=free,
        used_space_bytes=used,
        compression_enabled=bool(raw.get("compression_enabled", False)),
        bitlocker_status=map_bitlocker_status(raw.get("bitlocker_status")),
        volume_type=clean_str(raw.get("volume_type")),
        is_boot_volume=bool(raw.get("is_boot_volume", False)),
        is_system_volume=bool(raw.get("is_system_volume", False)),
        shadow_copy_support=bool(raw.get("shadow_copy_support", False))
    )

def map_raw_physical_disk(raw: Dict[str, Any]) -> PhysicalDiskInventoryData:
    
    media = raw.get("media_type")
    if isinstance(media, int):
        media = map_media_type(media)
    else:
        media = clean_str(media, "Unknown")
        
    bus = raw.get("bus_type")
    if isinstance(bus, int):
        bus = map_bus_type(bus)
    else:
        bus = clean_str(bus, "Unknown")

    return PhysicalDiskInventoryData(
        disk_number=int(raw.get("disk_number", 0)),
        model=clean_str(raw.get("model")),
        manufacturer=clean_str(raw.get("manufacturer")),
        serial_number=clean_str(raw.get("serial_number")),
        firmware_version=clean_str(raw.get("firmware_version")),
        media_type=media,
        bus_type=bus,
        interface_type=clean_str(raw.get("interface_type")),
        size_bytes=int(raw.get("size_bytes", 0)),
        partition_count=int(raw.get("partition_count", 0)),
        health_status=clean_str(raw.get("health_status")),
        operational_status=clean_str(raw.get("operational_status")),
        is_boot_disk=bool(raw.get("is_boot_disk", False)),
        is_system_disk=bool(raw.get("is_system_disk", False)),
        is_removable=bool(raw.get("is_removable", False)),
        is_virtual=bool(raw.get("is_virtual", False)),
        volumes=[map_raw_logical_volume(v) for v in raw.get("volumes", [])]
    )
