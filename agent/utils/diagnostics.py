import os
import sys
import json
import zipfile
import platform
import subprocess
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional

def collect_diagnostics_archive(output_dir: Optional[str] = None) -> str:
    """Collects logs, configuration, OS specs, services, and network adapter details into a timestamped ZIP archive."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    hostname = socket.gethostname()
    zip_filename = f"Sentinel_Diagnostics_{hostname}_{timestamp}.zip"

    if not output_dir:
        # Default to Desktop or User Profile
        user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
        desktop = os.path.join(user_profile, "Desktop")
        output_dir = desktop if os.path.exists(desktop) else user_profile

    os.makedirs(output_dir, exist_ok=True)
    zip_path = os.path.join(output_dir, zip_filename)

    # Determine paths
    prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
    agent_data_dir = os.path.join(prog_data, "EndpointSentinel")
    logs_dir = os.path.join(agent_data_dir, "logs")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Archive Log Files
        if os.path.exists(logs_dir):
            for root, _, files in os.walk(logs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join("logs", file)
                    zipf.write(file_path, arcname)

        # 2. Archive Safe Configuration Summary (Sanitizing raw tokens)
        config_path = os.path.join(agent_data_dir, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                # Sanitize secret
                if "enrollment_secret" in cfg:
                    cfg["enrollment_secret"] = "***REDACTED***"
                if "access_token" in cfg:
                    cfg["access_token"] = "***REDACTED***"
                
                safe_cfg_str = json.dumps(cfg, indent=2)
                zipf.writestr("config_summary.json", safe_cfg_str)
            except Exception as e:
                zipf.writestr("config_summary_error.txt", f"Error reading config: {e}")

        # 3. Collect Windows OS & System Specs
        os_info = f"""==================================================
ENDPOINT SENTINEL AGENT DIAGNOSTICS REPORT
==================================================
Generated At: {datetime.now().isoformat()}
Hostname: {hostname}
OS Platform: {platform.system()} {platform.release()}
OS Version: {platform.version()}
Architecture: {platform.machine()}
Python Executable: {sys.executable}
Python Version: {sys.version}
==================================================
"""
        zipf.writestr("system_info.txt", os_info)

        # 4. Collect Network Info (ipconfig /all)
        if os.name == "nt":
            try:
                net_output = subprocess.check_output("ipconfig /all", shell=True, text=True)
                zipf.writestr("network_ipconfig.txt", net_output)
            except Exception as e:
                zipf.writestr("network_ipconfig.txt", f"Error executing ipconfig: {e}")

            # 5. Collect Windows Services Status (sc query SentinelAgent)
            try:
                svc_output = subprocess.check_output("sc query SentinelAgent", shell=True, text=True)
                zipf.writestr("service_status.txt", svc_output)
            except Exception as e:
                zipf.writestr("service_status.txt", f"Error querying SentinelAgent service: {e}")

    return zip_path
