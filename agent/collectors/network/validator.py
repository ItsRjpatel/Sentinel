import re
import logging
from agent.collectors.network.models import NetworkAdapterInventoryData

logger = logging.getLogger(__name__)

MAC_REGEX = re.compile(r"^([0-9A-FA-F]{2}:){5}([0-9A-FA-F]{2})$")
IPV4_REGEX = re.compile(r"^([0-9]{1,3}\.){3}[0-9]{1,3}$")

def is_valid_mac(mac: str) -> bool:
    return bool(MAC_REGEX.match(mac))

def is_valid_ipv4(ip: str) -> bool:
    return bool(IPV4_REGEX.match(ip))


def should_collect_adapter(adapter: NetworkAdapterInventoryData) -> bool:
    """Applies strict filtering criteria to exclude loopback, inactive, or virtual hypervisor adapters."""
    name = adapter.adapter_name.lower()
    desc = adapter.adapter_description.lower()

    # 1. Ignore Disconnected / Disabled adapters
    if adapter.operational_status != "Connected":
        return False

    # 2. Ignore Loopback Interfaces
    if "loopback" in name or "loopback" in desc or adapter.ipv4 == "127.0.0.1" or adapter.ipv6 == "::1":
        return False

    # 3. Ignore Docker adapters
    if "docker" in name or "docker" in desc:
        return False

    # 4. Ignore Hyper-V Internal adapters
    if "hyper-v" in name or "hyper-v" in desc or "vethernet" in name:
        return False

    # 5. Ignore VirtualBox host-only adapters
    if "virtualbox" in name or "virtualbox" in desc or "vboxnet" in name:
        return False

    # 6. Basic sanity check on IP Address presence
    if adapter.ipv4 == "0.0.0.0" and adapter.ipv6 == "::":
        return False

    return True
