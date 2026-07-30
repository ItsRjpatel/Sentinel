import os
import logging
from typing import List, Dict, Any
from agent.collectors.storage.models import PhysicalDiskInventoryData
from agent.collectors.storage.mapper import map_raw_physical_disk
from agent.collectors.storage.validator import filter_invalid_disks

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

class StorageCollector:
    """Queries native Windows WMI tables to retrieve physical disk and logical volume telemetry."""

    def collect(self) -> List[PhysicalDiskInventoryData]:
        """Runs the WMI query collection routines and returns filtered, validated DTOs."""
        raw_disks: List[Dict[str, Any]] = []

        if not IS_WINDOWS:
            logger.info("Collector executing on non-Windows platform. Returning stub storage inventory data.")
            stub_records = [
                {
                    "disk_number": 0,
                    "model": "Stub NVMe Drive",
                    "manufacturer": "Stub Vendor",
                    "serial_number": "STUB12345",
                    "firmware_version": "1.0.0",
                    "media_type": 4, # SSD
                    "bus_type": 17,  # NVMe
                    "interface_type": "SCSI",
                    "size_bytes": 1000200000000,
                    "partition_count": 2,
                    "health_status": "Healthy",
                    "operational_status": "Online",
                    "is_boot_disk": True,
                    "is_system_disk": True,
                    "is_removable": False,
                    "is_virtual": False,
                    "volumes": [
                        {
                            "drive_letter": "C:",
                            "volume_name": "Windows",
                            "volume_guid": "{STUB-GUID-VOL1}",
                            "file_system": "NTFS",
                            "label": "Windows",
                            "capacity_bytes": 1000000000000,
                            "free_space_bytes": 500000000000,
                            "compression_enabled": False,
                            "bitlocker_status": 1, # Encrypted
                            "volume_type": "Local Disk",
                            "is_boot_volume": True,
                            "is_system_volume": True,
                            "shadow_copy_support": True
                        }
                    ]
                }
            ]
            dtos = [map_raw_physical_disk(r) for r in stub_records]
            return filter_invalid_disks(dtos)

        import win32com.client
        try:
            wmi = win32com.client.GetObject("winmgmts:")
        except Exception as e:
            logger.error(f"Failed to bind WMI engine COM objects: {e}")
            raise RuntimeError("WMI connection unavailable") from e

        # 1. Fetch Logical Disks
        logical_disks = {}
        try:
            for ld in wmi.ExecQuery("Select DeviceID, VolumeName, VolumeSerialNumber, FileSystem, Size, FreeSpace, Compressed, DriveType, VolumeDirty from Win32_LogicalDisk"):
                logical_disks[ld.DeviceID] = ld
        except Exception as e:
            logger.warning(f"Failed querying Win32_LogicalDisk: {e}")

        # 2. Fetch Volume details
        volumes_map = {}
        try:
            for vol in wmi.ExecQuery("Select DriveLetter, DeviceID, SystemVolume, BootVolume, Capacity, FreeSpace from Win32_Volume"):
                if vol.DriveLetter:
                    volumes_map[vol.DriveLetter] = vol
        except Exception as e:
            logger.warning(f"Failed querying Win32_Volume: {e}")

        # 3. Fetch Encryptable Volumes (BitLocker)
        bitlocker_map = {}
        try:
            bl_wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\CIMV2\\Security\\MicrosoftVolumeEncryption")
            for bl_vol in bl_wmi.ExecQuery("Select DriveLetter, ProtectionStatus from Win32_EncryptableVolume"):
                if bl_vol.DriveLetter:
                    bitlocker_map[bl_vol.DriveLetter] = bl_vol.ProtectionStatus
        except Exception as e:
            logger.debug(f"Failed querying BitLocker statuses (may need elevated permissions): {e}")

        # 4. Map Logical Disks to Partitions to Physical Disks
        disk_to_logical = {}
        try:
            for dp in wmi.ExecQuery("Select Antecedent, Dependent from Win32_LogicalDiskToPartition"):
                # Antecedent: \\MACHINE\root\cimv2:Win32_DiskPartition.DeviceID="Disk #0, Partition #1"
                # Dependent: \\MACHINE\root\cimv2:Win32_LogicalDisk.DeviceID="C:"
                ant = str(dp.Antecedent)
                dep = str(dp.Dependent)
                part_id = ant.split('="')[1].strip('"')
                drive_id = dep.split('="')[1].strip('"')
                disk_to_logical[part_id] = drive_id
        except Exception as e:
            logger.warning(f"Failed mapping logical disks to partitions: {e}")

        physical_to_partition = {}
        try:
            for ddp in wmi.ExecQuery("Select Antecedent, Dependent from Win32_DiskDriveToDiskPartition"):
                # Antecedent: \\MACHINE\root\cimv2:Win32_DiskDrive.DeviceID="\\\\.\\PHYSICALDRIVE0"
                # Dependent: \\MACHINE\root\cimv2:Win32_DiskPartition.DeviceID="Disk #0, Partition #1"
                ant = str(ddp.Antecedent)
                dep = str(ddp.Dependent)
                disk_id = ant.split('="')[1].strip('"').replace("\\", "").replace(".", "")
                part_id = dep.split('="')[1].strip('"')
                if disk_id not in physical_to_partition:
                    physical_to_partition[disk_id] = []
                physical_to_partition[disk_id].append(part_id)
        except Exception as e:
            logger.warning(f"Failed mapping physical disks to partitions: {e}")

        # 5. Fetch MSFT_Disk for deeper bus/media details
        msft_disk_map = {}
        try:
            st_wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\Microsoft\\Windows\\Storage")
            for msft_disk in st_wmi.ExecQuery("Select Number, MediaType, BusType, HealthStatus from MSFT_Disk"):
                try:
                    num = int(msft_disk.Number)
                    msft_disk_map[num] = msft_disk
                except (ValueError, TypeError):
                    continue
        except Exception as e:
            logger.debug(f"Failed querying MSFT_Disk: {e}")

        # 6. Fetch Physical Disks and assemble payload
        try:
            for pd in wmi.ExecQuery("Select DeviceID, Index, Model, Manufacturer, SerialNumber, FirmwareRevision, InterfaceType, Size, Partitions, Status, MediaType, Capabilities from Win32_DiskDrive"):
                try:
                    index = int(pd.Index)
                except (ValueError, TypeError):
                    continue
                
                dev_id_clean = str(pd.DeviceID).replace("\\", "").replace(".", "")
                msft = msft_disk_map.get(index)

                raw_disk = {
                    "disk_number": index,
                    "model": pd.Model,
                    "manufacturer": pd.Manufacturer,
                    "serial_number": pd.SerialNumber,
                    "firmware_version": pd.FirmwareRevision,
                    "media_type": msft.MediaType if msft else pd.MediaType,
                    "bus_type": msft.BusType if msft else None,
                    "interface_type": pd.InterfaceType,
                    "size_bytes": pd.Size,
                    "partition_count": pd.Partitions,
                    "health_status": msft.HealthStatus if msft else pd.Status,
                    "operational_status": pd.Status,
                    "is_removable": "Removable Media" in (pd.MediaType or ""),
                    "volumes": []
                }
                
                # Check Capabilities array for boot/system indicators if applicable (not entirely robust in WMI, relying on Volume mapping later)
                # Parse volumes
                part_ids = physical_to_partition.get(dev_id_clean, [])
                
                is_boot = False
                is_sys = False
                
                for part_id in part_ids:
                    drive_letter = disk_to_logical.get(part_id)
                    if not drive_letter:
                        continue
                        
                    ld = logical_disks.get(drive_letter)
                    vol = volumes_map.get(drive_letter)
                    if not ld:
                        continue

                    v_boot = vol.BootVolume if vol else False
                    v_sys = vol.SystemVolume if vol else False
                    if v_boot: is_boot = True
                    if v_sys: is_sys = True

                    raw_vol = {
                        "drive_letter": drive_letter,
                        "volume_name": ld.VolumeName,
                        "volume_guid": vol.DeviceID if vol else ld.VolumeSerialNumber,
                        "file_system": ld.FileSystem,
                        "label": ld.VolumeName,
                        "capacity_bytes": ld.Size,
                        "free_space_bytes": ld.FreeSpace,
                        "compression_enabled": ld.Compressed,
                        "bitlocker_status": bitlocker_map.get(drive_letter, 2), # 2 = unknown
                        "volume_type": "Local Disk" if ld.DriveType == 3 else "Network/Removable",
                        "is_boot_volume": v_boot,
                        "is_system_volume": v_sys,
                        "shadow_copy_support": True # Generic for NTFS/ReFS
                    }
                    raw_disk["volumes"].append(raw_vol)
                
                raw_disk["is_boot_disk"] = is_boot
                raw_disk["is_system_disk"] = is_sys
                
                raw_disks.append(raw_disk)
        except Exception as e:
            logger.warning(f"Failed querying Win32_DiskDrive: {e}")

        # Map and filter
        collected = []
        for raw in raw_disks:
            try:
                dto = map_raw_physical_disk(raw)
                collected.append(dto)
            except Exception as ex:
                logger.error(f"Error mapping storage properties: {ex}")

        for d in collected:
            logger.info(
                "Disk %s -> %d volumes",
                d.disk_number,
                len(d.volumes),
            )
        return filter_invalid_disks(collected)
