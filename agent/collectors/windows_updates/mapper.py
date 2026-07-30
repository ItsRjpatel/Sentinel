import re
import logging
from typing import Any, Dict
from agent.collectors.windows_updates.models import WindowsUpdateInventoryData

logger = logging.getLogger(__name__)

def clean_str(val: Any, default: str = "", max_len: int = 500) -> str:
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    return s[:max_len]

def extract_kb_number(raw_str: str) -> str:
    """Extracts KB identifier like 'KB5031234'."""
    if not raw_str:
        return ""
    
    match = re.search(r"(KB\d{6,8})", str(raw_str), re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return ""

def normalize_date(date_str: str) -> str:
    """Normalizes typical WMI/COM date formats into YYYY-MM-DD string."""
    if not date_str:
        return "Unknown"
    s = str(date_str).strip()
    # e.g., mm/dd/yyyy
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", s):
        parts = s.split("/")
        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    return s[:100]

def determine_flags(title: str, description: str, category: str):
    title_lower = title.lower()
    desc_lower = description.lower()
    cat_lower = category.lower()
    
    is_sec = "security" in title_lower or "security" in desc_lower or "security update" in cat_lower
    is_crit = "critical" in title_lower or "critical update" in cat_lower
    is_feat = "feature update" in title_lower or "upgrades" in cat_lower
    is_cumul = "cumulative update" in title_lower
    
    return is_sec, is_crit, is_feat, is_cumul

def map_wmi_quick_fix(raw: Dict[str, Any]) -> WindowsUpdateInventoryData:
    """Maps Win32_QuickFixEngineering records."""
    kb = extract_kb_number(raw.get("HotFixID", ""))
    desc = clean_str(raw.get("Description"), default="Update", max_len=1000)
    
    # WMI usually gives limited details
    title = f"{desc} ({kb})" if kb else desc
    installed_by = clean_str(raw.get("InstalledBy"), default="Unknown", max_len=255)
    installed_on = normalize_date(raw.get("InstalledOn", ""))
    
    is_sec, is_crit, is_feat, is_cumul = determine_flags(title, desc, desc)

    return WindowsUpdateInventoryData(
        kb_number=kb,
        title=title,
        description=desc,
        category=desc,  # WMI Description is often the category like 'Security Update'
        installed_by=installed_by,
        installed_on=installed_on,
        support_url=clean_str(raw.get("CSName"), default="", max_len=500), # Usually contains computer name, repurposed or empty
        update_id="",
        revision_number=0,
        operation_result="Succeeded",
        severity="Unknown",
        source="WMI",
        is_security_update=is_sec,
        is_critical_update=is_crit,
        is_feature_update=is_feat,
        is_cumulative_update=is_cumul,
        requires_restart=False,
        is_hidden=False,
        is_downloaded=True,
        installed_state="Installed"
    )

def map_com_update(raw: Dict[str, Any]) -> WindowsUpdateInventoryData:
    """Maps Microsoft.Update.Session COM objects."""
    title = clean_str(raw.get("Title"), default="Unknown Update", max_len=500)
    kb = extract_kb_number(title)
    if not kb:
        kbs = raw.get("KBArticleIDs", [])
        if kbs and len(kbs) > 0:
            kb = f"KB{kbs[0]}"

    desc = clean_str(raw.get("Description"), default="", max_len=1000)
    category = clean_str(raw.get("Category"), default="Updates", max_len=255)
    
    is_sec, is_crit, is_feat, is_cumul = determine_flags(title, desc, category)

    return WindowsUpdateInventoryData(
        kb_number=kb,
        title=title,
        description=desc,
        category=category,
        installed_by="NT AUTHORITY\\SYSTEM",
        installed_on=normalize_date(raw.get("LastDeploymentChangeTime", "")),
        support_url=clean_str(raw.get("SupportUrl"), default="", max_len=500),
        update_id=clean_str(raw.get("UpdateID"), default="", max_len=100),
        revision_number=int(raw.get("RevisionNumber", 0)),
        operation_result=clean_str(raw.get("OperationResult"), default="Succeeded", max_len=100),
        severity=clean_str(raw.get("MsrcSeverity"), default="Unknown", max_len=50),
        source="COM",
        is_security_update=is_sec,
        is_critical_update=is_crit,
        is_feature_update=is_feat,
        is_cumulative_update=is_cumul,
        requires_restart=bool(raw.get("RebootRequired", False)),
        is_hidden=bool(raw.get("IsHidden", False)),
        is_downloaded=bool(raw.get("IsDownloaded", True)),
        installed_state="Installed" if bool(raw.get("IsInstalled")) else "Unknown"
    )
