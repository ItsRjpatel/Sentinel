import logging
from agent.collectors.operating_system.models import OperatingSystemInventoryData

logger = logging.getLogger(__name__)

def validate_operating_system_data(data: OperatingSystemInventoryData) -> bool:
    """Performs semantic sanity checks on collected Operating System metrics."""
    
    # 1. Assert Computer Name is populated
    if not data.computer_name or data.computer_name == "Unknown":
        logger.warning("Anomaly detected: Operating System computer name is reporting missing/unknown chassis tags.")
        return False

    # 2. Assert non-negative uptime
    if data.uptime_seconds < 0:
        logger.warning(f"Anomaly detected: System uptime reports negative seconds ({data.uptime_seconds}).")
        return False

    # 3. Assert system directory exists in paths
    if "System32" not in data.system_directory and data.system_directory != "Unknown":
        logger.warning(f"Anomaly detected: Unusual Windows system directory paths detected ({data.system_directory}).")

    return True
