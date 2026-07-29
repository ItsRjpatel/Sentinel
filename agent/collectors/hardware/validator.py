import logging
from agent.collectors.hardware.models import HardwareInventoryData

logger = logging.getLogger(__name__)

def validate_hardware_data(data: HardwareInventoryData) -> bool:
    """Performs semantic sanity checks on collected hardware inventory metrics."""
    
    # 1. Assert CPU Core consistency
    if data.cpu_logical_processors < data.cpu_cores:
        logger.warning(
            f"Anomaly detected: CPU logical processors ({data.cpu_logical_processors}) "
            f"is less than physical cores ({data.cpu_cores})."
        )
        return False

    # 2. Assert positive memory allocation
    if data.installed_ram_bytes <= 0:
        logger.warning(f"Anomaly detected: Installed RAM is reporting zero/negative bytes ({data.installed_ram_bytes}).")
        return False

    # 3. Assert basic identification tags
    if data.manufacturer == "Unknown" and data.model == "Unknown":
        logger.warning("Anomaly detected: Endpoint is reporting completely unidentified chassis tags.")
        return False

    return True
