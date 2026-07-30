import logging
from typing import Any, Dict
from agent.collectors.operating_system.models import OperatingSystemInventoryData

logger = logging.getLogger(__name__)

PRODUCT_TYPE_MAP = {
    1: "Workstation",
    2: "Domain Controller",
    3: "Server"
}

def map_raw_operating_system(raw: Dict[str, Any]) -> OperatingSystemInventoryData:
    """Transforms raw dictionary properties from WMI/registry to a validated Pydantic model."""
    
    # 1. Resolve Product Type description
    p_type = raw.get("product_type")
    product_type_str = "Unknown"
    if p_type is not None:
        try:
            p_type_int = int(p_type)
            product_type_str = PRODUCT_TYPE_MAP.get(p_type_int, f"Unknown ({p_type_int})")
        except ValueError:
            product_type_str = str(p_type)

    def clean_str(val: Any, default: str = "Unknown") -> str:
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    return OperatingSystemInventoryData(
        computer_name=clean_str(raw.get("computer_name")),
        os_name=clean_str(raw.get("os_name")),
        edition=clean_str(raw.get("edition")),
        version=clean_str(raw.get("version")),
        build_number=clean_str(raw.get("build_number")),
        display_version=clean_str(raw.get("display_version")),
        install_date=clean_str(raw.get("install_date")),
        last_boot_time=clean_str(raw.get("last_boot_time")),
        uptime_seconds=int(raw.get("uptime_seconds", 0)),
        system_architecture=clean_str(raw.get("system_architecture")),
        product_type=product_type_str,
        registered_owner=clean_str(raw.get("registered_owner")),
        registered_organization=clean_str(raw.get("registered_organization")),
        windows_directory=clean_str(raw.get("windows_directory")),
        system_directory=clean_str(raw.get("system_directory")),
        boot_device=clean_str(raw.get("boot_device")),
        system_drive=clean_str(raw.get("system_drive")),
        locale=clean_str(raw.get("locale")),
        time_zone=clean_str(raw.get("time_zone")),
        domain_workgroup=clean_str(raw.get("domain_workgroup")),
        activation_status=clean_str(raw.get("activation_status"), "Unknown")
    )
