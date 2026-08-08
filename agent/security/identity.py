import os
import uuid
import hashlib
import logging
from typing import Any, Dict, Optional
from agent.utils.storage import StorageProvider

logger = logging.getLogger(__name__)

def get_registry_machine_guid() -> str:
    """Fallback query to HKLM Registry for MachineGuid if WMI BIOS queries fail."""
    if os.name != "nt":
        return "fallback-machine-uuid"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
            val, _ = winreg.QueryValueEx(key, "MachineGuid")
            return str(val).strip()
    except Exception as e:
        logger.warning(f"Failed to query HKLM MachineGuid from registry: {e}")
        return "fallback-machine-uuid"


def get_hardware_identifiers() -> Dict[str, str]:
    """Retrieve primary hardware constants directly through WMI APIs without calling wmic.exe."""
    identifiers = {
        "bios_uuid": "",
        "cpu_id": "",
        "motherboard_serial": "",
        "mac_address": ""
    }

    if os.name == "nt":
        try:
            import win32com.client
            # Bind to WMI service namespace
            wmi_service = win32com.client.GetObject("winmgmts:")
            
            # 1. BIOS UUID
            products = wmi_service.ExecQuery("Select UUID from Win32_ComputerSystemProduct")
            for p in products:
                if p.UUID:
                    identifiers["bios_uuid"] = str(p.UUID).strip()
                    break
            
            # 2. CPU ID
            processors = wmi_service.ExecQuery("Select ProcessorId from Win32_Processor")
            for proc in processors:
                if proc.ProcessorId:
                    identifiers["cpu_id"] = str(proc.ProcessorId).strip()
                    break

            # 3. Motherboard Serial
            boards = wmi_service.ExecQuery("Select SerialNumber from Win32_BaseBoard")
            for b in boards:
                if b.SerialNumber:
                    identifiers["motherboard_serial"] = str(b.SerialNumber).strip()
                    break

            # 4. Primary MAC Address
            adapters = wmi_service.ExecQuery(
                "Select MACAddress from Win32_NetworkAdapterConfiguration where IPEnabled=True"
            )
            for a in adapters:
                if a.MACAddress:
                    identifiers["mac_address"] = str(a.MACAddress).strip()
                    break
        except Exception as e:
            logger.warning(f"WMI native queries failed: {e}")

    # Fallbacks for virtualization or non-Windows tests
    if not identifiers["bios_uuid"] or identifiers["bios_uuid"].lower() == "ffffffff-ffff-ffff-ffff-ffffffffffff":
        identifiers["bios_uuid"] = get_registry_machine_guid()

    if not identifiers["mac_address"]:
        fallback_node = uuid.getnode()
        identifiers["mac_address"] = ':'.join(
            ("%012X" % fallback_node)[i:i+2] for i in range(0, 12, 2)
        )

    return identifiers


def generate_machine_fingerprint() -> str:
    """Generates a stable, unique SHA-256 fingerprint identifying the physical endpoint."""
    ids = get_hardware_identifiers()
    raw_sig = f"{ids['bios_uuid']}|{ids['cpu_id']}|{ids['motherboard_serial']}"
    return hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()


class AgentIdentity:
    """Representation of the Agent Identity state."""

    def __init__(
        self,
        machine_fingerprint: str,
        installation_id: str,
        agent_uuid: str,
        identity_version: int = 1
    ) -> None:
        self.machine_fingerprint = machine_fingerprint
        self.installation_id = installation_id
        self.agent_uuid = agent_uuid
        self.identity_version = identity_version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "machine_fingerprint": self.machine_fingerprint,
            "installation_id": self.installation_id,
            "agent_uuid": self.agent_uuid,
            "identity_version": self.identity_version
        }


async def load_or_create_identity(storage: StorageProvider) -> AgentIdentity:
    """Loads identity parameters from secure storage, or registers a new hardware fingerprint."""
    data = await storage.read("identity")
    
    if data and data.get("agent_uuid"):
        return AgentIdentity(
            machine_fingerprint=data.get("machine_fingerprint", ""),
            installation_id=data.get("installation_id", ""),
            agent_uuid=data.get("agent_uuid"),
            identity_version=data.get("identity_version", 1)
        )
    
    # Generate new identity parameters
    fingerprint = generate_machine_fingerprint()
    install_id = str(uuid.uuid4())
    agent_id = str(uuid.uuid4())
    
    identity = AgentIdentity(
        machine_fingerprint=fingerprint,
        installation_id=install_id,
        agent_uuid=agent_id,
        identity_version=1
    )
    
    await storage.write("identity", identity.to_dict())
    return identity
