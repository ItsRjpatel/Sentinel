import logging
from typing import List
from agent.collectors.storage.models import PhysicalDiskInventoryData, LogicalVolumeInventoryData

logger = logging.getLogger(__name__)

def is_valid_drive_letter(letter: str) -> bool:
    """Checks if drive letter matches format 'C:'"""
    if not letter:
        return False
    if len(letter) == 2 and letter[0].isalpha() and letter[1] == ':':
        return True
    return False

def filter_invalid_volumes(volumes: List[LogicalVolumeInventoryData]) -> List[LogicalVolumeInventoryData]:
    valid_volumes = []
    seen_drive_letters = set()

    for vol in volumes:
        # 1. Invalid drive letters
        if not is_valid_drive_letter(vol.drive_letter):
            continue
        if vol.drive_letter in seen_drive_letters:
            continue
            
        # 2. Negative capacities
        if vol.capacity_bytes < 0 or vol.free_space_bytes < 0 or vol.used_space_bytes < 0:
            continue
            
        # 3. Unknown filesystem values
        if vol.file_system.lower() in ["unknown", ""]:
            continue

        valid_volumes.append(vol)
        seen_drive_letters.add(vol.drive_letter)

    return valid_volumes


def filter_invalid_disks(disks: List[PhysicalDiskInventoryData]) -> List[PhysicalDiskInventoryData]:
    valid_disks = []
    seen_serials = set()

    for disk in disks:
        # 1. Reject duplicate serial numbers
        if disk.serial_number in seen_serials or not disk.serial_number or disk.serial_number.lower() == "unknown":
            continue
            
        # 2. Ignore CD/DVD drives
        if "CD" in disk.media_type or "DVD" in disk.media_type or disk.bus_type == "ATAPI":
            continue
            
        # 3. Ignore disconnected removable media
        if disk.is_removable and disk.operational_status.lower() not in ["online", "ok"]:
            continue

        # Clean nested volumes
        disk.volumes = filter_invalid_volumes(disk.volumes)

        valid_disks.append(disk)
        seen_serials.add(disk.serial_number)

    return valid_disks
