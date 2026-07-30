import os
import datetime
import logging
from typing import Dict, Any
from agent.collectors.operating_system.models import OperatingSystemInventoryData
from agent.collectors.operating_system.mapper import map_raw_operating_system
from agent.collectors.operating_system.validator import validate_operating_system_data

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"


class OperatingSystemCollector:
    """Queries native Windows WMI tables and registry to retrieve endpoint Operating System details."""

    def collect(self) -> OperatingSystemInventoryData:
        """Runs the collection routines and returns a validated Pydantic DTO."""
        raw_data: Dict[str, Any] = {}

        if not IS_WINDOWS:
            # Stub values for cross-platform local developer environments (like MacOS/Linux)
            logger.info("Collector executing on non-Windows platform. Returning stub operating system inventory data.")
            raw_data = {
                "computer_name": "Standard-Dev-Host",
                "os_name": "Microsoft Windows 11 Enterprise (Stub)",
                "edition": "Enterprise",
                "version": "10.0.22621",
                "build_number": "22621",
                "display_version": "22H2",
                "install_date": "20231015092040.000000+120",
                "last_boot_time": "20260728100532.000000+330",
                "uptime_seconds": 86400,
                "system_architecture": "64-bit",
                "product_type": 1,
                "registered_owner": "Developer Account",
                "registered_organization": "DevOrg",
                "windows_directory": "C:\\Windows",
                "system_directory": "C:\\Windows\\System32",
                "boot_device": "\\Device\\HarddiskVolume1",
                "system_drive": "C:",
                "locale": "0409",
                "time_zone": "UTC+5:30",
                "domain_workgroup": "WORKGROUP",
                "activation_status": "Licensed (Activated)"
            }
            return map_raw_operating_system(raw_data)

        import win32com.client
        import winreg

        # 1. Connect to WMI root\CIMV2 namespace
        try:
            wmi = win32com.client.GetObject("winmgmts:")
        except Exception as e:
            logger.error(f"Failed to bind WMI engine COM objects: {e}")
            raise RuntimeError("WMI connection unavailable") from e

        # Query Win32_OperatingSystem
        raw_boot_time = None
        try:
            query = (
                "Select CSName, Caption, Version, BuildNumber, InstallDate, LastBootUpTime, "
                "OSArchitecture, ProductType, RegisteredUser, Organization, WindowsDirectory, "
                "SystemDirectory, BootDevice, Locale from Win32_OperatingSystem"
            )
            for os_obj in wmi.ExecQuery(query):
                raw_data["computer_name"] = os_obj.CSName
                raw_data["os_name"] = os_obj.Caption
                raw_data["version"] = os_obj.Version
                raw_data["build_number"] = os_obj.BuildNumber
                raw_data["install_date"] = os_obj.InstallDate
                raw_data["last_boot_time"] = os_obj.LastBootUpTime
                raw_data["system_architecture"] = os_obj.OSArchitecture
                raw_data["product_type"] = os_obj.ProductType
                raw_data["registered_owner"] = os_obj.RegisteredUser
                raw_data["registered_organization"] = os_obj.Organization
                raw_data["windows_directory"] = os_obj.WindowsDirectory
                raw_data["system_directory"] = os_obj.SystemDirectory
                raw_data["boot_device"] = os_obj.BootDevice
                raw_data["locale"] = os_obj.Locale
                
                raw_boot_time = os_obj.LastBootUpTime
                
                # Derive System Drive
                if os_obj.SystemDirectory and ":" in os_obj.SystemDirectory:
                    raw_data["system_drive"] = os_obj.SystemDirectory.split(":")[0] + ":"
                else:
                    raw_data["system_drive"] = "C:"
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_OperatingSystem: {e}")

        # Compute Uptime
        if raw_boot_time:
            try:
                # Parse WMI Timestamp (YYYYMMDDHHMMSS.mmmmmm+UUU)
                dt_str = raw_boot_time.split(".")[0]
                dt = datetime.datetime.strptime(dt_str, "%Y%m%d%H%M%S")
                
                sign = 1
                if "-" in raw_boot_time:
                    offset_str = raw_boot_time.split("-")[-1]
                    sign = -1
                else:
                    offset_str = raw_boot_time.split("+")[-1] if "+" in raw_boot_time else None
                
                tz = datetime.timezone.utc
                if offset_str:
                    try:
                        # Extract first 3 numeric characters of offset (minutes)
                        minutes = int(offset_str[:3]) * sign
                        tz = datetime.timezone(datetime.timedelta(minutes=minutes))
                    except ValueError:
                        pass
                
                boot_dt = dt.replace(tzinfo=tz)
                now_dt = datetime.datetime.now(datetime.timezone.utc)
                raw_data["uptime_seconds"] = max(0, int((now_dt - boot_dt).total_seconds()))
            except Exception as e:
                logger.warning(f"Failed to parse OS boot time: {e}")
                raw_data["uptime_seconds"] = 0
        else:
            raw_data["uptime_seconds"] = 0

        # Query Win32_ComputerSystem for Domain / Workgroup
        try:
            for cs in wmi.ExecQuery("Select Domain, PartOfDomain from Win32_ComputerSystem"):
                raw_data["domain_workgroup"] = cs.Domain if cs.Domain else "WORKGROUP"
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_ComputerSystem: {e}")

        # Query Win32_TimeZone for Timezone display name
        try:
            for tz_obj in wmi.ExecQuery("Select Caption from Win32_TimeZone"):
                raw_data["time_zone"] = tz_obj.Caption
                break
        except Exception as e:
            logger.warning(f"Failed to query Win32_TimeZone: {e}")
            raw_data["time_zone"] = "UTC"

        # 2. Query Registry for Display Version & Edition
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            try:
                raw_data["display_version"], _ = winreg.QueryValueEx(key, "DisplayVersion")
            except FileNotFoundError:
                try:
                    raw_data["display_version"], _ = winreg.QueryValueEx(key, "ReleaseId")
                except FileNotFoundError:
                    raw_data["display_version"] = "Unknown"
            
            try:
                raw_data["edition"], _ = winreg.QueryValueEx(key, "EditionID")
            except FileNotFoundError:
                raw_data["edition"] = "Unknown"
        except Exception as e:
            logger.warning(f"Failed to read display version/edition from registry: {e}")
            raw_data["display_version"] = "Unknown"
            raw_data["edition"] = "Unknown"

        # 3. Query Activation Status via SoftwareLicensingProduct (licensed state)
        try:
            # SoftwareLicensingProduct application ID for Windows is 55c92734-d682-4d71-983e-d6ef31105918
            license_statuses = {
                0: "Unlicensed",
                1: "Licensed (Activated)",
                2: "OOBGrace",
                3: "OOTGrace",
                4: "NonGenuineGrace",
                5: "Notification",
                6: "ExtendedGrace"
            }
            query = (
                "Select LicenseStatus from SoftwareLicensingProduct "
                "where ApplicationID = '55c92734-d682-4d71-983e-d6ef31105918' "
                "and PartialProductKey is not Null"
            )
            for prod in wmi.ExecQuery(query):
                raw_data["activation_status"] = license_statuses.get(
                    prod.LicenseStatus, f"Unknown ({prod.LicenseStatus})"
                )
                break
        except Exception as e:
            logger.info(f"Activation status query bypassed: {e}")
            raw_data["activation_status"] = "Unknown"

        # Map and validate
        dto = map_raw_operating_system(raw_data)
        validate_operating_system_data(dto)
        return dto
