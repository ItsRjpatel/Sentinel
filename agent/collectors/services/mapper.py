import logging
from typing import Any, Dict
from agent.collectors.services.models import WindowsServiceInventoryData

logger = logging.getLogger(__name__)

def clean_str(val: Any, default: str = "", max_len: int = 500) -> str:
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    return s[:max_len]

def map_wmi_service(raw: Dict[str, Any]) -> WindowsServiceInventoryData:
    """Maps Win32_Service records to WindowsServiceInventoryData DTO."""
    
    # State normalization
    state = clean_str(raw.get("State"), default="Unknown", max_len=50)
    
    # StartMode normalization
    start_mode = clean_str(raw.get("StartMode"), default="Unknown", max_len=50)
    
    service_type = clean_str(raw.get("ServiceType"), default="Unknown", max_len=100)
    
    return WindowsServiceInventoryData(
        service_name=clean_str(raw.get("Name"), default="Unknown", max_len=255),
        display_name=clean_str(raw.get("DisplayName"), default="Unknown", max_len=500),
        description=clean_str(raw.get("Description"), default="", max_len=1000),
        executable_path=clean_str(raw.get("PathName"), default="", max_len=1000),
        current_state=state,
        start_mode=start_mode,
        start_type=start_mode, # often StartMode and StartType are synonymous in WMI mappings unless querying registry directly
        service_type=service_type,
        account_name=clean_str(raw.get("StartName"), default="LocalSystem", max_len=255),
        process_id=int(raw.get("ProcessId", 0) or 0),
        binary_path=clean_str(raw.get("PathName"), default="", max_len=1000),
        delayed_auto_start=bool(raw.get("DelayedAutoStart", False)),
        error_control=clean_str(raw.get("ErrorControl"), default="Normal", max_len=50),
        dependencies="", # WMI Win32_Service doesn't cleanly expose this without WMI associations
        dependent_services="", 
        can_stop=bool(raw.get("AcceptStop", False)),
        can_pause=bool(raw.get("AcceptPause", False)),
        can_shutdown=bool(raw.get("AcceptStop", False)), # WMI doesn't explicitly have AcceptShutdown in Win32_Service often
        desktop_interaction=bool(raw.get("DesktopInteract", False)),
        tag_id=int(raw.get("TagId", 0) or 0),
        is_critical=False, # Would require querying Service Control Manager directly
        digital_signature_status="Unknown" # Would require Authenticode verification of binary_path
    )
