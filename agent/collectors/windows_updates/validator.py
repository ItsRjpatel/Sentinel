import logging
from typing import List, Dict, Any
from agent.collectors.windows_updates.models import WindowsUpdateInventoryData

logger = logging.getLogger(__name__)

def is_valid_update_entry(dto: WindowsUpdateInventoryData) -> bool:
    # 1. Reject if no KB Number is resolvable
    if not dto.kb_number or dto.kb_number.strip() == "" or dto.kb_number.lower() == "unknown":
        # WMI might return 'File 1' as a hotfix ID, which is invalid
        if not dto.kb_number.startswith("KB"):
            return False

    # 2. Reject incomplete records without basic titles/descriptions
    if not dto.title and not dto.description:
        return False

    # 3. Reject if not successfully installed (COM API tracks this in installed_state)
    if dto.installed_state.lower() != "installed":
        return False

    return True


def filter_windows_updates(
    raw_wmi_entries: List[Dict[str, Any]],
    raw_com_entries: List[Dict[str, Any]],
    map_wmi_func,
    map_com_func
) -> List[WindowsUpdateInventoryData]:
    """Processes both data sources, prioritizes COM over WMI, and removes duplicates."""
    valid_list: List[WindowsUpdateInventoryData] = []
    seen_kbs = set()

    # Process COM first as it contains richer metadata (Category, Severity, GUIDs)
    for raw in raw_com_entries:
        try:
            dto = map_com_func(raw)
            if not is_valid_update_entry(dto):
                continue
            
            kb_upper = dto.kb_number.upper()
            if kb_upper in seen_kbs:
                continue
            
            valid_list.append(dto)
            seen_kbs.add(kb_upper)
        except Exception as e:
            logger.debug(f"Skipping COM update entry due to mapping error: {e}")

    # Process WMI as fallback for updates not visible in COM session
    for raw in raw_wmi_entries:
        try:
            dto = map_wmi_func(raw)
            if not is_valid_update_entry(dto):
                continue
            
            kb_upper = dto.kb_number.upper()
            if kb_upper in seen_kbs:
                continue
            
            valid_list.append(dto)
            seen_kbs.add(kb_upper)
        except Exception as e:
            logger.debug(f"Skipping WMI update entry due to mapping error: {e}")

    return valid_list
