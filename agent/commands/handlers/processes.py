import psutil
import logging

logger = logging.getLogger(__name__)

def execute(command: dict) -> dict:
    """Handles the GET_PROCESS_LIST command."""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                # Calculate memory in MB
                mem_mb = info['memory_info'].rss / (1024 * 1024) if info.get('memory_info') else 0
                
                processes.append({
                    "pid": int(info.get("pid") or 0),
                    "name": str(info.get("name") or "Unknown"),
                    "cpu": float(info.get("cpu_percent", 0.0) or 0.0),
                    "memory_mb": float(round(mem_mb, 2))
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return {"success": True, "processes": processes}
    except Exception as e:
        logger.error(f"Error getting process list: {e}")
        return {"success": False, "error": str(e)}
