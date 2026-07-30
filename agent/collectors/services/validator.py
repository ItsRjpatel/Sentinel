import logging
from typing import List, Dict, Any
from agent.collectors.services.models import WindowsServiceInventoryData

logger = logging.getLogger(__name__)

def is_valid_service_entry(dto: WindowsServiceInventoryData) -> bool:
    # 1. Reject if no valid service name
    if not dto.service_name or dto.service_name.strip() == "" or dto.service_name.lower() == "unknown":
        return False

    # 2. Ignore temporary services (often end with _<hex_string> created per-user session)
    # e.g., CDPUserSvc_1a2b3c
    import re
    if re.search(r"_[0-9a-fA-F]{4,8}$", dto.service_name):
        return False

    # 3. Ignore driver services (unless configurable, user said ignore driver services)
    if dto.service_type.lower() in ["kernel driver", "file system driver"]:
        return False
        
    return True

def filter_windows_services(
    raw_wmi_entries: List[Dict[str, Any]],
    map_wmi_func
) -> List[WindowsServiceInventoryData]:
    """Processes WMI data sources and removes duplicates or invalid services."""
    valid_list: List[WindowsServiceInventoryData] = []
    seen_names = set()

    for raw in raw_wmi_entries:
        try:
            dto = map_wmi_func(raw)
            if not is_valid_service_entry(dto):
                continue
            
            name_lower = dto.service_name.lower()
            if name_lower in seen_names:
                continue
            
            valid_list.append(dto)
            seen_names.add(name_lower)
        except Exception as e:
            logger.debug(f"Skipping WMI service entry due to mapping error: {e}")

    return valid_list
