import logging
from typing import Any, Dict
from agent.collectors.hardware.models import HardwareInventoryData

logger = logging.getLogger(__name__)

CPU_ARCH_MAP = {
    0: "x86",
    1: "MIPS",
    2: "Alpha",
    3: "PowerPC",
    5: "ARM",
    6: "Itanium",
    9: "x64",
    12: "ARM64"
}

def map_raw_hardware(raw: Dict[str, Any]) -> HardwareInventoryData:
    """Transforms raw dictionary properties from WMI/registry to a validated Pydantic model."""
    
    # 1. Resolve CPU Architecture
    raw_arch = raw.get("cpu_architecture")
    arch_str = "Unknown"
    if raw_arch is not None:
        try:
            arch_int = int(raw_arch)
            arch_str = CPU_ARCH_MAP.get(arch_int, f"Unknown ({arch_int})")
        except ValueError:
            arch_str = str(raw_arch)

    # 2. Virtual Machine Detection logic
    model = str(raw.get("model", "")).lower()
    manufacturer = str(raw.get("manufacturer", "")).lower()
    is_virtual = False
    
    vm_indicators = [
        "virtualbox", "vmware", "kvm", "qemu", "virtual machine",
        "hyper-v", "xen", "hvm", "parallels", "microsoft corporation virtual"
    ]
    if any(indicator in model or indicator in manufacturer for indicator in vm_indicators):
        is_virtual = True

    # 3. Handle default string formats
    def clean_str(val: Any, default: str = "Unknown") -> str:
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    return HardwareInventoryData(
        manufacturer=clean_str(raw.get("manufacturer")),
        model=clean_str(raw.get("model")),
        serial_number=clean_str(raw.get("serial_number")),
        bios_version=clean_str(raw.get("bios_version")),
        bios_manufacturer=clean_str(raw.get("bios_manufacturer")),
        bios_release_date=clean_str(raw.get("bios_release_date")),
        motherboard=clean_str(raw.get("motherboard")),
        cpu_name=clean_str(raw.get("cpu_name")),
        cpu_architecture=arch_str,
        cpu_cores=int(raw.get("cpu_cores", 1)),
        cpu_logical_processors=int(raw.get("cpu_logical_processors", 1)),
        installed_ram_bytes=int(raw.get("installed_ram_bytes", 0)),
        tpm_version=raw.get("tpm_version") if raw.get("tpm_version") else None,
        secure_boot_enabled=bool(raw.get("secure_boot_enabled", False)),
        is_virtual=is_virtual
    )
