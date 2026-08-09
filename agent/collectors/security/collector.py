import os
import logging
import subprocess
import json
from typing import Dict, Any
from agent.collectors.security.models import SecurityInventoryData
from agent.collectors.security.mapper import map_raw_security
from agent.collectors.security.validator import validate_security_data

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

class SecurityCollector:
    """Queries Windows Defender and Firewall status."""

    def collect(self) -> SecurityInventoryData:
        raw_data: Dict[str, Any] = {
            "defender_enabled": False,
            "real_time_protection_enabled": False,
            "defender_service_status": "Unknown",
            "antivirus_signature_version": "Unknown",
            "firewall_domain_enabled": False,
            "firewall_private_enabled": False,
            "firewall_public_enabled": False
        }
        
        if not IS_WINDOWS:
            logger.info("Collector executing on non-Windows platform. Returning stub security data.")
            raw_data = {
                "defender_enabled": True,
                "real_time_protection_enabled": True,
                "defender_service_status": "Running",
                "antivirus_signature_version": "1.0.0.0",
                "firewall_domain_enabled": True,
                "firewall_private_enabled": True,
                "firewall_public_enabled": True
            }
            return map_raw_security(raw_data)

        # 1. Defender Status via PowerShell Get-MpComputerStatus
        try:
            ps_command = 'Get-MpComputerStatus | Select-Object AMServiceEnabled, RealTimeProtectionEnabled, AntivirusSignatureVersion | ConvertTo-Json'
            result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                defender_data = json.loads(result.stdout.strip())
                raw_data["defender_enabled"] = bool(defender_data.get("AMServiceEnabled", False))
                raw_data["real_time_protection_enabled"] = bool(defender_data.get("RealTimeProtectionEnabled", False))
                raw_data["antivirus_signature_version"] = str(defender_data.get("AntivirusSignatureVersion", "Unknown"))
        except Exception as e:
            logger.warning(f"Failed to query Defender status: {e}")

        # 2. Firewall Status via Get-NetFirewallProfile
        try:
            ps_command = 'Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json'
            result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                fw_data = json.loads(result.stdout.strip())
                # Handle single object vs list return from ConvertTo-Json
                if isinstance(fw_data, dict):
                    fw_data = [fw_data]
                for profile in fw_data:
                    name = profile.get("Name")
                    enabled = profile.get("Enabled") == 1  # 1 = True, 2 = False, etc. OR boolean True
                    # ConvertTo-Json sometimes parses enum as int, sometimes as bool
                    if isinstance(profile.get("Enabled"), bool):
                        enabled = profile.get("Enabled")
                    if name == "Domain":
                        raw_data["firewall_domain_enabled"] = bool(enabled)
                    elif name == "Private":
                        raw_data["firewall_private_enabled"] = bool(enabled)
                    elif name == "Public":
                        raw_data["firewall_public_enabled"] = bool(enabled)
        except Exception as e:
            logger.warning(f"Failed to query Firewall status: {e}")

        # 3. Defender Service Status via Get-Service
        try:
            ps_command = 'Get-Service WinDefend | Select-Object Status | ConvertTo-Json'
            result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                svc_data = json.loads(result.stdout.strip())
                # Status Enum: 1=Stopped, 2=StartPending, 3=StopPending, 4=Running, etc.
                status_val = svc_data.get("Status")
                if status_val == 4:
                    raw_data["defender_service_status"] = "Running"
                elif status_val == 1:
                    raw_data["defender_service_status"] = "Stopped"
                else:
                    raw_data["defender_service_status"] = str(status_val)
        except Exception as e:
            logger.warning(f"Failed to query WinDefend service status: {e}")

        return map_raw_security(raw_data)
