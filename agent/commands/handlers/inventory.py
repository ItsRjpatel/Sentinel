import time
import logging

from agent.collectors.hardware.collector import HardwareCollector
from agent.collectors.operating_system.collector import OperatingSystemCollector
from agent.collectors.network.collector import NetworkCollector
from agent.collectors.storage.collector import StorageCollector
from agent.collectors.software.collector import SoftwareCollector
from agent.collectors.windows_updates.collector import WindowsUpdateCollector
from agent.collectors.services.collector import WindowsServiceCollector

logger = logging.getLogger(__name__)

def execute(command: dict) -> dict:
    """Handles the RUN_INVENTORY command by executing all collectors."""
    start_time = time.time()
    
    result = {
        "success": False,
        "hardware": False,
        "os": False,
        "network": False,
        "storage": False,
        "software": False,
        "windows_updates": False,
        "services": False,
        "duration_ms": 0
    }
    
    collectors = [
        ("hardware", HardwareCollector()),
        ("os", OperatingSystemCollector()),
        ("network", NetworkCollector()),
        ("storage", StorageCollector()),
        ("software", SoftwareCollector()),
        ("windows_updates", WindowsUpdateCollector()),
        ("services", WindowsServiceCollector()),
    ]
    
    all_success = True
    for key, collector in collectors:
        try:
            # We just execute them to ensure they can run. 
            # Output is normally uploaded by the scheduler task, but here we just collect it.
            # Real implementation might upload, but requirement says "No upload yet. Result upload is Sprint 4 Phase 4."
            collector.collect()
            result[key] = True
        except Exception as e:
            logger.error(f"Collector {key} failed during RUN_INVENTORY command: {e}")
            result[key] = False
            all_success = False

    result["success"] = all_success
    result["duration_ms"] = int((time.time() - start_time) * 1000)
    
    return result
