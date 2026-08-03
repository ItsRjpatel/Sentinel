import subprocess
import logging
import re
import psutil

logger = logging.getLogger(__name__)

def is_valid_service_name(name: str) -> bool:
    """Validates the service name to prevent command injection."""
    return bool(re.match(r"^[a-zA-Z0-9_\- ]+$", name))

def handle_restart_service(command: dict) -> dict:
    """Handles the RESTART_SERVICE command."""
    payload = command.get("payload", {})
    service_name = payload.get("service_name")
    
    if not service_name or not is_valid_service_name(service_name):
        return {"success": False, "error": "Invalid or missing service_name in payload"}

    try:
        # We use subprocess to stop and start the service
        # sc.exe stop "service_name"
        subprocess.run(["sc.exe", "stop", service_name], check=False, capture_output=True, text=True)
        # sc.exe start "service_name"
        start_res = subprocess.run(["sc.exe", "start", service_name], check=False, capture_output=True, text=True)
        
        return {
            "success": start_res.returncode == 0 or "started" in start_res.stdout.lower() or "already running" in start_res.stdout.lower(),
            "service": service_name,
            "stdout": start_res.stdout.strip(),
            "stderr": start_res.stderr.strip()
        }
    except Exception as e:
        logger.error(f"Error restarting service {service_name}: {e}")
        return {"success": False, "error": str(e)}

def handle_get_service_list(command: dict) -> dict:
    """Handles the GET_SERVICE_LIST command."""
    services = []
    try:
        for svc in psutil.win_service_iter():
            try:
                # Some services might not be fully queryable, so we fallback
                info = {}
                try:
                    info = svc.as_dict()
                except Exception:
                    info = {"name": svc.name(), "display_name": svc.display_name()}
                    
                services.append({
                    "name": str(info.get("name") or "Unknown"),
                    "display_name": str(info.get("display_name") or "Unknown"),
                    "status": str(info.get("status", "unknown")),
                    "start_type": str(info.get("start_type", "unknown"))
                })
            except Exception:
                pass
        return {"success": True, "services": services}
    except Exception as e:
        logger.error(f"Error getting service list: {e}")
        return {"success": False, "error": str(e)}
