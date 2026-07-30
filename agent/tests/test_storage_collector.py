import pytest
from unittest.mock import MagicMock, patch
from agent.collectors.storage.models import PhysicalDiskInventoryData, LogicalVolumeInventoryData
from agent.collectors.storage.mapper import map_raw_physical_disk, map_raw_logical_volume, map_bitlocker_status, map_media_type, map_bus_type
from agent.collectors.storage.validator import filter_invalid_disks
from agent.scheduler.storage_task import DiskInventoryTask

def test_map_raw_logical_volume():
    raw_vol = {
        "capacity_bytes": "1000",
        "free_space_bytes": "200",
        "drive_letter": "C:",
        "volume_name": "Win",
        "volume_guid": "{test}",
        "file_system": "NTFS",
        "label": "Win",
        "compression_enabled": True,
        "bitlocker_status": 1,
        "volume_type": "Local Disk",
        "is_boot_volume": True,
        "is_system_volume": True,
        "shadow_copy_support": True
    }
    
    dto = map_raw_logical_volume(raw_vol)
    assert dto.capacity_bytes == 1000
    assert dto.free_space_bytes == 200
    assert dto.used_space_bytes == 800
    assert dto.drive_letter == "C:"
    assert dto.bitlocker_status == "Encrypted"


def test_map_raw_physical_disk():
    raw_disk = {
        "disk_number": 0,
        "model": "TEST SSD",
        "manufacturer": "TEST",
        "serial_number": "SN123",
        "firmware_version": "1.0",
        "media_type": 4, # SSD
        "bus_type": 17, # NVMe
        "interface_type": "SCSI",
        "size_bytes": 500,
        "partition_count": 2,
        "health_status": "Healthy",
        "operational_status": "Online",
        "is_boot_disk": True,
        "is_system_disk": True,
        "is_removable": False,
        "is_virtual": False,
        "volumes": []
    }
    
    dto = map_raw_physical_disk(raw_disk)
    assert dto.media_type == "SSD"
    assert dto.bus_type == "NVMe"
    assert dto.serial_number == "SN123"
    assert len(dto.volumes) == 0


def test_validator_filtering():
    vol_valid = LogicalVolumeInventoryData(
        drive_letter="C:",
        volume_name="Windows",
        volume_guid="123",
        file_system="NTFS",
        label="Windows",
        capacity_bytes=1000,
        free_space_bytes=500,
        used_space_bytes=500,
        compression_enabled=False,
        bitlocker_status="Encrypted",
        volume_type="Local",
        is_boot_volume=True,
        is_system_volume=True,
        shadow_copy_support=True
    )
    
    vol_invalid_letter = vol_valid.model_copy(update={"drive_letter": "INVALID"})
    vol_negative_cap = vol_valid.model_copy(update={"capacity_bytes": -1})
    vol_unknown_fs = vol_valid.model_copy(update={"file_system": "Unknown"})

    disk_valid = PhysicalDiskInventoryData(
        disk_number=0,
        model="Test",
        manufacturer="Test",
        serial_number="VALID_SN",
        firmware_version="1.0",
        media_type="SSD",
        bus_type="NVMe",
        interface_type="SCSI",
        size_bytes=1000,
        partition_count=1,
        health_status="Healthy",
        operational_status="Online",
        is_boot_disk=True,
        is_system_disk=True,
        is_removable=False,
        is_virtual=False,
        volumes=[vol_valid, vol_invalid_letter, vol_negative_cap, vol_unknown_fs, vol_valid.model_copy(update={"volume_guid": "dup"})] # add dup letter
    )

    disk_dup = disk_valid.model_copy(update={"disk_number": 1}) # same SN, should be dropped
    
    disk_cd = disk_valid.model_copy(update={
        "serial_number": "CD_SN",
        "media_type": "CD-ROM",
        "bus_type": "ATAPI"
    })
    
    disk_disconnected_usb = disk_valid.model_copy(update={
        "serial_number": "USB_SN",
        "is_removable": True,
        "operational_status": "Offline"
    })

    disks = [disk_valid, disk_dup, disk_cd, disk_disconnected_usb]
    filtered = filter_invalid_disks(disks)
    
    assert len(filtered) == 1
    valid = filtered[0]
    assert valid.serial_number == "VALID_SN"
    assert len(valid.volumes) == 1 # invalid volumes dropped
    assert valid.volumes[0].drive_letter == "C:"


@pytest.mark.asyncio
async def test_storage_task_execution():
    client_mock = AsyncMock()
    client_mock.request.return_value.status_code = 200
    
    enrollment_mock = AsyncMock()
    enrollment_mock.is_enrolled.return_value = True
    
    collector_mock = MagicMock()
    collector_mock.collect.return_value = [
        PhysicalDiskInventoryData(
            disk_number=0,
            model="Stub",
            manufacturer="Stub Vendor",
            serial_number="SN123",
            firmware_version="1.0",
            media_type="SSD",
            bus_type="NVMe",
            interface_type="SCSI",
            size_bytes=1000,
            partition_count=1,
            health_status="Healthy",
            operational_status="Online",
            is_boot_disk=True,
            is_system_disk=True,
            is_removable=False,
            is_virtual=False,
            volumes=[]
        )
    ]
    
    task = DiskInventoryTask(interval_seconds=60, client=client_mock, enrollment_manager=enrollment_mock, collector=collector_mock)
    await task.execute()
    
    client_mock.request.assert_called_once()
    args, kwargs = client_mock.request.call_args
    assert kwargs["path"] == "inventory/storage"
    payload = kwargs["json_data"]
    assert len(payload) == 1
    assert payload[0]["serial_number"] == "SN123"


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
