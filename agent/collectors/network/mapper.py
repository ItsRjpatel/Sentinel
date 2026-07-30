import logging
from typing import Any, Dict
from agent.collectors.network.models import NetworkAdapterInventoryData

logger = logging.getLogger(__name__)

CONN_STATUS_MAP = {
    0: "Disconnected",
    1: "Connecting",
    2: "Connected",
    3: "Disconnecting",
    4: "Hardware Not Present",
    5: "Hardware Disabled",
    6: "Hardware Malfunction",
    7: "Media Disconnected",
    8: "Authenticating",
    9: "Authentication Succeeded",
    10: "Authentication Failed",
    11: "Invalid Address",
    12: "Credentials Required"
}

def format_mac(mac: Any) -> Optional[str]:
    """Converts raw MAC strings to standardized uppercase colon-delimited format."""
    if not mac:
        return None
    s = str(mac).replace("-", "").replace(":", "").strip().upper()
    if len(s) == 12:
        return ":".join(s[i:i+2] for i in range(0, 12, 2))
    return s


def map_raw_network_adapter(raw: Dict[str, Any]) -> NetworkAdapterInventoryData:
    """Transforms raw dictionary properties from WMI to a validated Pydantic model."""
    
    # 1. Map Operational Status
    status_code = raw.get("operational_status")
    status_str = "Unknown"
    if status_code is not None:
        try:
            status_int = int(status_code)
            status_str = CONN_STATUS_MAP.get(status_int, f"Unknown ({status_int})")
        except ValueError:
            status_str = str(status_code)

    # 2. Connection Type Classifications
    name = str(raw.get("adapter_name", "")).lower()
    desc = str(raw.get("adapter_description", "")).lower()
    
    is_vpn = False
    vpn_signals = ["vpn", "tap", "tun", "cisco", "openvpn", "wireguard", "fortinet", "globalprotect", "secure shield"]
    if any(sig in name or sig in desc for sig in vpn_signals):
        is_vpn = True

    connection_type = "Ethernet"
    wifi_signals = ["wireless", "wi-fi", "wifi", "802.11", "wlan"]
    if any(sig in name or sig in desc for sig in wifi_signals):
        connection_type = "WiFi"
    elif is_vpn:
        connection_type = "VPN"

    def clean_str(val: Any, default: str = "Unknown") -> str:
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    return NetworkAdapterInventoryData(
        hostname=clean_str(raw.get("hostname")),
        domain_workgroup=clean_str(raw.get("domain_workgroup")),
        adapter_name=clean_str(raw.get("adapter_name")),
        adapter_description=clean_str(raw.get("adapter_description")),
        interface_guid=clean_str(raw.get("interface_guid")),
        mac_address=format_mac(raw.get("mac_address")),
        ipv4=clean_str(raw.get("ipv4"), "0.0.0.0"),
        ipv6=clean_str(raw.get("ipv6"), "::"),
        subnet_mask=clean_str(raw.get("subnet_mask"), "255.255.255.0"),
        gateway=clean_str(raw.get("gateway"), "0.0.0.0"),
        dns_servers=clean_str(raw.get("dns_servers"), "8.8.8.8"),
        dhcp_enabled=bool(raw.get("dhcp_enabled", False)),
        dhcp_server=clean_str(raw.get("dhcp_server"), "0.0.0.0"),
        lease_obtained=clean_str(raw.get("lease_obtained"), ""),
        lease_expires=clean_str(raw.get("lease_expires"), ""),
        interface_speed=int(raw.get("interface_speed", 0)),
        interface_type=clean_str(raw.get("interface_type")),
        operational_status=status_str,
        is_physical=bool(raw.get("is_physical", False)),
        connection_type=connection_type,
        is_vpn=is_vpn
    )
