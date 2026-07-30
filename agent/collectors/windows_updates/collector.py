import os
import logging
from typing import List, Dict, Any
from agent.collectors.windows_updates.models import WindowsUpdateInventoryData
from agent.collectors.windows_updates.mapper import map_wmi_quick_fix, map_com_update
from agent.collectors.windows_updates.validator import filter_windows_updates

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

class WindowsUpdateCollector:
    """Discovers installed Windows Updates using COM (Microsoft.Update.Session) and WMI (Win32_QuickFixEngineering)."""

    def _query_wmi(self) -> List[Dict[str, Any]]:
        raw_list = []
        if not IS_WINDOWS:
            return raw_list
            
        try:
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            serv = wmi.ConnectServer(".", "root\\CIMV2")
            qfe_items = serv.ExecQuery("SELECT * FROM Win32_QuickFixEngineering")
            for item in qfe_items:
                raw_list.append({
                    "HotFixID": getattr(item, "HotFixID", ""),
                    "Description": getattr(item, "Description", ""),
                    "InstalledBy": getattr(item, "InstalledBy", ""),
                    "InstalledOn": getattr(item, "InstalledOn", ""),
                    "CSName": getattr(item, "CSName", "")
                })
        except Exception as e:
            logger.warning(f"Failed to query WMI Win32_QuickFixEngineering: {e}")
            
        return raw_list

    def _query_com(self) -> List[Dict[str, Any]]:
        raw_list = []
        if not IS_WINDOWS:
            return raw_list
            
        try:
            import win32com.client
            # Initialize Microsoft Update Session
            update_session = win32com.client.Dispatch("Microsoft.Update.Session")
            update_searcher = update_session.CreateUpdateSearcher()
            # IsInstalled=1 returns only installed updates
            # IsHidden=0 avoids listing intentionally suppressed updates (though we can collect them)
            search_result = update_searcher.Search("IsInstalled=1")
            
            updates = search_result.Updates
            for i in range(updates.Count):
                update = updates.Item(i)
                identity = update.Identity
                
                # Fetch KB Article IDs
                kbs = []
                for j in range(update.KBArticleIDs.Count):
                    kbs.append(update.KBArticleIDs.Item(j))
                
                raw_list.append({
                    "Title": getattr(update, "Title", ""),
                    "Description": getattr(update, "Description", ""),
                    "LastDeploymentChangeTime": getattr(update, "LastDeploymentChangeTime", ""),
                    "SupportUrl": getattr(update, "SupportUrl", ""),
                    "UpdateID": getattr(identity, "UpdateID", ""),
                    "RevisionNumber": getattr(identity, "RevisionNumber", 0),
                    "OperationResult": "Succeeded", # Assumed succeeded if IsInstalled=1
                    "MsrcSeverity": getattr(update, "MsrcSeverity", ""),
                    "RebootRequired": getattr(update, "RebootRequired", False),
                    "IsHidden": getattr(update, "IsHidden", False),
                    "IsDownloaded": getattr(update, "IsDownloaded", True),
                    "IsInstalled": getattr(update, "IsInstalled", True),
                    "KBArticleIDs": kbs,
                    # Fallbacks for category (complex object in COM)
                    "Category": "Windows Update"
                })
        except Exception as e:
            logger.warning(f"Failed to query COM Microsoft.Update.Session: {e}")
            
        return raw_list

    def collect(self) -> List[WindowsUpdateInventoryData]:
        """Queries WMI and COM APIs and returns a deduplicated, validated DTO list."""
        if not IS_WINDOWS:
            logger.info("Collector executing on non-Windows platform. Returning stub windows updates.")
            stub_com = [{
                "Title": "Cumulative Update for Windows 11 (KB5031234)",
                "KBArticleIDs": ["5031234"],
                "IsInstalled": True
            }]
            stub_wmi = [{
                "HotFixID": "KB5045678",
                "Description": "Security Update",
                "InstalledOn": "03/01/2026"
            }]
            return filter_windows_updates(stub_wmi, stub_com, map_wmi_quick_fix, map_com_update)

        raw_com = self._query_com()
        raw_wmi = self._query_wmi()

        return filter_windows_updates(raw_wmi, raw_com, map_wmi_quick_fix, map_com_update)
