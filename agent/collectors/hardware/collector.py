import os
import logging
from typing import Dict, Any
from agent.collectors.hardware.models import HardwareInventoryData
from agent.collectors.hardware.mapper import map_raw_hardware
from agent.collectors.hardware.validator import validate_hardware_data

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"


class HardwareCollector:
    """Queries native Windows WMI tables and registry to retrieve endpoint hardware specifications."""

    def collect(self) -> HardwareInventoryData:
        """Runs the collection routines and returns a validated Pydantic DTO."""
        raw_data: Dict[str, Any] = {}
        
        if not IS_WINDOWS:
            # Stub values for cross-platform local developer environments (like MacOS/Linux)
            logger.info("Collector executing on non-Windows platform. Returning stub inventory data.")
            raw_data = {
                "manufacturer": "Standard Dev Platform",
                "model": "Local Developer Instance",
                "serial_number": "DEV-123456",
                "bios_version": "V1.0-DEV",
                "bios_manufacturer": "DevBios",
                "bios_release_date": "2026-07-29",
                "motherboard": "DevBoard-XYZ",
                "cpu_name": "Dev CPU @ 2.50GHz",
                "cpu_architecture": 9,  # x64
                "cpu_cores": 4,
                "cpu_logical_processors": 8,
                "installed_ram_bytes": 17179869184,  # 16 GB in bytes
                "tpm_version": None,
                "secure_boot_enabled": False,
                "is_virtual": True
            }
            return map_raw_hardware(raw_data)

        import win32com.client
        import winreg

        # 1. Connect to WMI root\CIMV2 namespace
        try:
            wmi = win32com.client.GetObject("winmgmts:")
        except Exception as e:
            logger.error(f"Failed to bind WMI engine COM objects: {e}")
            raise RuntimeError("WMI connection unavailable") from e

        # Query Win32_ComputerSystem
        try:
            for sys_obj in wmi.ExecQuery("Select Manufacturer, Model, TotalPhysicalMemory from Win32_ComputerSystem"):
                raw_data["manufacturer"] = sys_obj.Manufacturer
                raw_data["model"] = sys_obj.Model
                raw_data["installed_ram_bytes"] = sys_obj.TotalPhysicalMemory
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_ComputerSystem: {e}")

        # Query Win32_BaseBoard
        try:
            for board in wmi.ExecQuery("Select SerialNumber, Product from Win32_BaseBoard"):
                raw_data["serial_number"] = board.SerialNumber
                raw_data["motherboard"] = board.Product
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_BaseBoard: {e}")

        # Query Win32_BIOS
        try:
            for bios in wmi.ExecQuery("Select Version, SMBIOSBIOSVersion, Manufacturer, ReleaseDate from Win32_BIOS"):
                raw_data["bios_version"] = bios.SMBIOSBIOSVersion if bios.SMBIOSBIOSVersion else bios.Version
                raw_data["bios_manufacturer"] = bios.Manufacturer
                raw_data["bios_release_date"] = bios.ReleaseDate
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_BIOS: {e}")

        # Query Win32_Processor
        try:
            for proc in wmi.ExecQuery("Select Name, Architecture, NumberOfCores, NumberOfLogicalProcessors from Win32_Processor"):
                raw_data["cpu_name"] = proc.Name
                raw_data["cpu_architecture"] = proc.Architecture
                raw_data["cpu_cores"] = proc.NumberOfCores
                raw_data["cpu_logical_processors"] = proc.NumberOfLogicalProcessors
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_Processor: {e}")

        # 2. Query TPM via Security WMI namespace (requires fallback/ignoring access denials)
        try:
            wmi_tpm = win32com.client.GetObject("winmgmts:\\\\.\\root\\CIMV2\\Security\\MicrosoftTpm")
            for tpm in wmi_tpm.ExecQuery("Select SpecVersion from Win32_Tpm"):
                raw_data["tpm_version"] = tpm.SpecVersion
                break
        except Exception as e:
            logger.info(f"TPM details query bypassed (likely access restricted or TPM disabled): {e}")
            raw_data["tpm_version"] = None

        # 3. Query Registry for Secure Boot
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SecureBoot\State")
            val, _ = winreg.QueryValueEx(key, "UEFISecureBootEnabled")
            raw_data["secure_boot_enabled"] = (val == 1)
        except Exception as e:
            logger.info(f"SecureBoot query bypassed (SecureBoot key missing in registry): {e}")
            raw_data["secure_boot_enabled"] = False

        # Map and validate DTO
        dto = map_raw_hardware(raw_data)
        validate_hardware_data(dto)
        return dto
