import os
import logging
from typing import List, Dict, Any
from agent.collectors.services.models import WindowsServiceInventoryData
from agent.collectors.services.mapper import map_wmi_service
from agent.collectors.services.validator import filter_windows_services

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

class WindowsServiceCollector:
    """Discovers installed Windows Services using WMI (Win32_Service)."""

    def _query_wmi(self) -> List[Dict[str, Any]]:
        raw_list = []
        if not IS_WINDOWS:
            return raw_list
            
        try:
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            serv = wmi.ConnectServer(".", "root\\CIMV2")
            service_items = serv.ExecQuery("SELECT * FROM Win32_Service")
            for item in service_items:
                raw_list.append({
                    "Name": getattr(item, "Name", ""),
                    "DisplayName": getattr(item, "DisplayName", ""),
                    "Description": getattr(item, "Description", ""),
                    "PathName": getattr(item, "PathName", ""),
                    "State": getattr(item, "State", ""),
                    "StartMode": getattr(item, "StartMode", ""),
                    "ServiceType": getattr(item, "ServiceType", ""),
                    "StartName": getattr(item, "StartName", ""),
                    "ProcessId": getattr(item, "ProcessId", 0),
                    "DelayedAutoStart": getattr(item, "DelayedAutoStart", False),
                    "ErrorControl": getattr(item, "ErrorControl", ""),
                    "AcceptStop": getattr(item, "AcceptStop", False),
                    "AcceptPause": getattr(item, "AcceptPause", False),
                    "DesktopInteract": getattr(item, "DesktopInteract", False),
                    "TagId": getattr(item, "TagId", 0)
                })
        except Exception as e:
            logger.warning(f"Failed to query WMI Win32_Service: {e}")
            
        return raw_list

    def collect(self) -> List[WindowsServiceInventoryData]:
        """Queries WMI APIs and returns a deduplicated, validated DTO list."""
        if not IS_WINDOWS:
            logger.info("Collector executing on non-Windows platform. Returning stub windows services.")
            stub_wmi = [{
                "Name": "Spooler",
                "DisplayName": "Print Spooler",
                "Description": "This service spools print jobs.",
                "PathName": "C:\\Windows\\System32\\spoolsv.exe",
                "State": "Running",
                "StartMode": "Auto",
                "ServiceType": "Own Process",
                "StartName": "LocalSystem"
            }]
            return filter_windows_services(stub_wmi, map_wmi_service)

        raw_wmi = self._query_wmi()
        return filter_windows_services(raw_wmi, map_wmi_service)
