import re
import logging
from typing import List, Dict, Any
from agent.collectors.software.models import SoftwareInventoryData

logger = logging.getLogger(__name__)

# Exclusion regex patterns for Windows Updates, Hotfixes, Language Packs, Drivers, etc.
KB_UPDATE_PATTERN = re.compile(r"\b(KB\d{6,8})\b", re.IGNORECASE)
UPDATE_KEYWORDS = [
    "security update",
    "update for microsoft",
    "hotfix",
    "servicing stack",
    "cumulative update"
]

LANG_PACK_KEYWORDS = [
    "language pack",
    "mui pack",
    "local experience pack",
    "lip pack"
]

DRIVER_KEYWORDS = [
    "driver package",
    "realtek high definition audio driver",
    "intel(r) graphics driver",
    "nvidia graphics driver"
]


def is_windows_update(app_name: str, raw_entry: Dict[str, Any] = None) -> bool:
    if KB_UPDATE_PATTERN.search(app_name):
        return True
    name_lower = app_name.lower()
    for kw in UPDATE_KEYWORDS:
        if kw in name_lower:
            return True
    if raw_entry and raw_entry.get("ParentKeyName"):
        return True
    return False


def is_language_pack(app_name: str) -> bool:
    name_lower = app_name.lower()
    for kw in LANG_PACK_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def is_driver(app_name: str, publisher: str) -> bool:
    name_lower = app_name.lower()
    for kw in DRIVER_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def is_valid_software_entry(dto: SoftwareInventoryData, raw_entry: Dict[str, Any] = None) -> bool:
    # 1. Reject entries without DisplayName / application_name
    if not dto.application_name or dto.application_name.strip() == "" or dto.application_name == "Unknown":
        return False

    # 2. Reject hidden system components
    if dto.system_component:
        return False
    if raw_entry and (raw_entry.get("SystemComponent") == 1 or str(raw_entry.get("SystemComponent")).lower() == "true"):
        return False

    # 3. Reject Windows Updates / Hotfixes
    if is_windows_update(dto.application_name, raw_entry):
        return False

    # 4. Reject Language Packs
    if is_language_pack(dto.application_name):
        return False

    # 5. Reject Drivers
    if is_driver(dto.application_name, dto.publisher):
        return False

    return True


def filter_software_list(
    raw_entries: List[Dict[str, Any]],
    map_func
) -> List[SoftwareInventoryData]:
    valid_list: List[SoftwareInventoryData] = []
    seen_keys = set()

    for raw in raw_entries:
        try:
            dto = map_func(raw)
            if not is_valid_software_entry(dto, raw):
                continue

            # Deduplicate by (application_name, publisher, version)
            dedup_key = (dto.application_name.lower(), dto.publisher.lower(), dto.version.lower())
            if dedup_key in seen_keys:
                continue

            valid_list.append(dto)
            seen_keys.add(dedup_key)
        except Exception as e:
            logger.debug(f"Skipping software entry due to mapping/validation error: {e}")

    return valid_list
