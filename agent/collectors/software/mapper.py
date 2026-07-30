import re
import logging
from typing import Any, Dict
from agent.collectors.software.models import SoftwareInventoryData

logger = logging.getLogger(__name__)

def clean_str(val: Any, default: str = "Unknown", max_len: int = 255) -> str:
    if val is None:
        return default
    s = str(val).strip()
    if not s:
        return default
    return s[:max_len]

def normalize_version(ver: Any) -> str:
    s = clean_str(ver, default="1.0.0", max_len=100)
    if s == "Unknown":
        return "1.0.0"
    return s

def normalize_install_date(date_str: Any) -> str:
    """Normalizes registry InstallDate formats like 'YYYYMMDD' to 'YYYY-MM-DD'."""
    if not date_str:
        return "Unknown"
    s = str(date_str).strip()
    # Check YYYYMMDD format
    if re.match(r"^\d{8}$", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s[:50]

def normalize_publisher(pub: Any) -> str:
    s = clean_str(pub, default="Unknown Publisher", max_len=255)
    # Common normalization cleanups
    s_lower = s.lower()
    if "microsoft" in s_lower:
        return "Microsoft Corporation"
    if "google" in s_lower:
        return "Google LLC"
    if "oracle" in s_lower:
        return "Oracle Corporation"
    if "adobe" in s_lower:
        return "Adobe Inc."
    return s

def normalize_architecture(arch: Any, hive_path: str = "") -> str:
    if arch and str(arch).strip():
        a = str(arch).strip().lower()
        if "64" in a or "x64" in a or "amd64" in a:
            return "x64"
        if "86" in a or "x86" in a or "32" in a:
            return "x86"
        if "arm64" in a:
            return "ARM64"
    if "wow6432node" in hive_path.lower():
        return "x86"
    return "x64"


def map_raw_registry_entry(raw: Dict[str, Any]) -> SoftwareInventoryData:
    app_name = clean_str(raw.get("DisplayName"), default="", max_len=255)
    publisher = normalize_publisher(raw.get("Publisher"))
    version = normalize_version(raw.get("DisplayVersion"))
    install_date = normalize_install_date(raw.get("InstallDate"))
    install_location = clean_str(raw.get("InstallLocation"), default="", max_len=500)
    
    try:
        est_size = int(raw.get("EstimatedSize", 0))
        if est_size < 0:
            est_size = 0
    except (ValueError, TypeError):
        est_size = 0

    uninstall_string = clean_str(raw.get("UninstallString"), default="", max_len=500)
    install_source = clean_str(raw.get("InstallSource"), default="", max_len=500)
    architecture = normalize_architecture(raw.get("Architecture"), raw.get("RegistryKey", ""))
    language = clean_str(raw.get("Language"), default="1033", max_len=50)
    product_code = clean_str(raw.get("ProductCode"), default="", max_len=100)

    try:
        sys_comp = bool(int(raw.get("SystemComponent", 0)))
    except (ValueError, TypeError):
        sys_comp = False

    try:
        win_inst = bool(int(raw.get("WindowsInstaller", 0)))
    except (ValueError, TypeError):
        win_inst = False

    url_info = clean_str(raw.get("URLInfoAbout"), default="", max_len=500)
    help_link = clean_str(raw.get("HelpLink"), default="", max_len=500)
    modify_path = clean_str(raw.get("ModifyPath"), default="", max_len=500)
    install_scope = clean_str(raw.get("InstallScope"), default="Per-machine", max_len=50)
    registry_key = clean_str(raw.get("RegistryKey"), default="", max_len=500)

    return SoftwareInventoryData(
        application_name=app_name,
        publisher=publisher,
        version=version,
        install_date=install_date,
        install_location=install_location,
        estimated_size_kb=est_size,
        uninstall_string=uninstall_string,
        install_source=install_source,
        architecture=architecture,
        language=language,
        product_code=product_code,
        system_component=sys_comp,
        windows_installer=win_inst,
        url_info=url_info,
        help_link=help_link,
        modify_path=modify_path,
        install_scope=install_scope,
        registry_key=registry_key
    )
