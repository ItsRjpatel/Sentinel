import os
import sys
import argparse
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional
from agent.utils.config import load_settings
from agent.utils.logging import setup_logging
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.utils.container import Container
from agent.security.identity import load_or_create_identity
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager
from agent.scheduler.scheduler import Scheduler
from agent.scheduler.heartbeat import HeartbeatTask
from agent.collectors.hardware.collector import HardwareCollector
from agent.collectors.operating_system.collector import OperatingSystemCollector
from agent.collectors.network.collector import NetworkCollector
from agent.collectors.storage.collector import StorageCollector
from agent.collectors.software.collector import SoftwareCollector
from agent.scheduler.hardware_task import HardwareInventoryTask
from agent.scheduler.os_task import OperatingSystemInventoryTask
from agent.scheduler.network_task import NetworkInventoryTask
from agent.scheduler.storage_task import DiskInventoryTask
from agent.scheduler.software_task import SoftwareInventoryTask
from agent.collectors.windows_updates.collector import WindowsUpdateCollector
from agent.scheduler.windows_update_task import WindowsUpdateInventoryTask
from agent.collectors.services.collector import WindowsServiceCollector
from agent.scheduler.services_task import WindowsServiceInventoryTask
from agent.scheduler.command_polling_task import CommandPollingTask

logger = logging.getLogger("agent.main")

# Global stop event for async service running in console/foreground mode
_stop_event: Optional[asyncio.Event] = None


async def async_service_start() -> None:
    """Bootstrap root method initializing DI, logs, credentials, and check-in loops."""
    global _stop_event
    _stop_event = asyncio.Event()

    # 1. Load Configurations and Initialize Rotating JSON Logging
    config = load_settings()
    setup_logging(config.get_log_file_path(), config.log_level)
    
    logger.info("Initializing Sentinel Agent bootstrap sequence...")

    # 2. Instantiate DI container and secure DPAPI file storage
    container = Container.get_instance()
    container.config = config
    container.storage = DPAPIJSONStorageProvider(config.get_data_dir())
    
    # 3. Create Identity if it doesn't exist
    identity = await load_or_create_identity(container.storage)
    logger.info(f"Loaded machine fingerprint: {identity.machine_fingerprint}")

    # 4. Instantiate transport HTTP client
    container.http_client = AgentHTTPClient(
        base_url=config.server_url,
        storage=container.storage,
        verify_tls=config.verify_tls
    )

    if not config.verify_tls:
        logger.warning("TLS Verification is DISABLED via config. Production communication may be insecure.")

    # 5. Initialize Enrollment Service
    container.enrollment_service = EnrollmentManager(
        client=container.http_client,
        storage=container.storage,
        enrollment_secret=config.enrollment_secret
    )

    # 6. Execute Enrollment if not enrolled
    if not await container.enrollment_service.is_enrolled():
        logger.info("Agent is unregistered. Running enrollment handshake...")
        try:
            await container.enrollment_service.enroll()
        except Exception as e:
            logger.error(f"Initial enrollment failed: {e}. Retry scheduled on heartbeat loop.")

    # 7. Initialize Heartbeat, Hardware Collector, and Scheduler Container
    container.heartbeat_service = HeartbeatTask(
        interval_seconds=config.heartbeat_interval_seconds,
        client=container.http_client,
        storage=container.storage,
        enrollment_manager=container.enrollment_service,
        config_version=config.config_version
    )

    collector = HardwareCollector()
    container.hardware_inventory_task = HardwareInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=collector
    )

    os_collector = OperatingSystemCollector()
    container.os_inventory_task = OperatingSystemInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=os_collector
    )

    net_collector = NetworkCollector()
    container.net_inventory_task = NetworkInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=net_collector
    )

    storage_collector = StorageCollector()
    container.storage_inventory_task = DiskInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=storage_collector
    )

    software_collector = SoftwareCollector()
    container.software_inventory_task = SoftwareInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=software_collector
    )

    wu_collector = WindowsUpdateCollector()
    container.windows_update_task = WindowsUpdateInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=wu_collector
    )

    ws_collector = WindowsServiceCollector()
    container.windows_service_task = WindowsServiceInventoryTask(
        interval_seconds=86400,
        client=container.http_client,
        enrollment_manager=container.enrollment_service,
        collector=ws_collector
    )

    container.command_polling_task = CommandPollingTask(
        backend_client=container.http_client,
        interval_seconds=10
    )

    container.scheduler = Scheduler()
    container.scheduler.register_task(container.heartbeat_service)
    container.scheduler.register_task(container.command_polling_task)
    container.scheduler.register_task(container.hardware_inventory_task)
    container.scheduler.register_task(container.os_inventory_task)
    container.scheduler.register_task(container.net_inventory_task)
    container.scheduler.register_task(container.storage_inventory_task)
    container.scheduler.register_task(container.software_inventory_task)
    container.scheduler.register_task(container.windows_update_task)
    container.scheduler.register_task(container.windows_service_task)

    # 8. Start Async Scheduler execution loop and run initial collection immediately
    await container.scheduler.start()
    asyncio.create_task(container.hardware_inventory_task.execute())
    asyncio.create_task(container.os_inventory_task.execute())
    asyncio.create_task(container.net_inventory_task.execute())
    asyncio.create_task(container.storage_inventory_task.execute())
    asyncio.create_task(container.software_inventory_task.execute())
    asyncio.create_task(container.windows_update_task.execute())
    asyncio.create_task(container.windows_service_task.execute())
    logger.info("Sentinel Agent successfully started.")

    # Block thread until stop signal is sent
    await _stop_event.wait()
    
    # Graceful cleanup
    logger.info("Shutting down Sentinel Agent service...")
    await container.scheduler.stop()
    await container.http_client.close()
    logger.info("Sentinel Agent shutdown completed.")


def setup_installer_logging() -> str:
    """Sets up emergency installer logger writing to %TEMP%\\SentinelInstaller.log and stdout."""
    temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Windows\\Temp"))
    log_path = os.path.join(temp_dir, "SentinelInstaller.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_path


def _is_admin() -> bool:
    """Check if the current process has Administrator privileges."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _request_elevation() -> None:
    """Re-launch the current process with UAC elevation (Run as Administrator)."""
    import ctypes
    logger.info("Requesting UAC elevation for installer...")
    if getattr(sys, "frozen", False):
        exe = sys.executable
        params = " ".join(sys.argv[1:])
    else:
        exe = sys.executable
        params = " ".join([f'"{arg}"' for arg in sys.argv])
    
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe, params, None, 1
    )
    if result <= 32:
        logger.error(f"UAC elevation request failed with code: {result}")
    sys.exit(0)


def run_service_manager() -> None:
    """Main execution dispatcher handling GUI Wizard, Silent Install, Service SCM, and Uninstaller."""
    log_path = setup_installer_logging()
    logger.info(f"Sentinel Agent Setup starting... (Log file: {log_path})")

    try:
        argv = sys.argv[1:]
        
        # 1. Double-clicked or launched with no arguments -> Launch GUI Enrollment Wizard
        if not argv:
            # Request admin privileges for service installation
            if os.name == "nt" and not _is_admin():
                logger.info("Not running as Administrator. Requesting UAC elevation...")
                _request_elevation()
                return
            
            logger.info("Running as Administrator. Launching GUI Enrollment Wizard...")
            from agent.installer.wizard import SentinelEnrollmentWizard
            wizard = SentinelEnrollmentWizard()
            wizard.run()
            return

        first_arg = argv[0].lower()

        # 2. Silent Uninstaller
        if first_arg in ("/uninstall", "uninstall"):
            if os.name == "nt" and not _is_admin():
                _request_elevation()
                return
            logger.info("Uninstall switch detected. Launching Uninstaller...")
            from agent.installer.uninstaller import run_uninstaller
            keep_cfg = "--keep-config" in argv
            run_uninstaller(keep_config=keep_cfg)
            return

        # 3. Silent Installation
        if first_arg in ("/s", "/silent", "--silent"):
            if os.name == "nt" and not _is_admin():
                _request_elevation()
                return
            logger.info("Silent installation switch detected...")
            server_url = "http://127.0.0.1:8000"
            token = "sentinel-secret-key-change-in-production"
            department = "IT Operations"

            for arg in argv:
                if arg.lower().startswith("/server="):
                    server_url = arg.split("=", 1)[1]
                elif arg.lower().startswith("/token="):
                    token = arg.split("=", 1)[1]
                elif arg.lower().startswith("/dept="):
                    department = arg.split("=", 1)[1]

            logger.info(f"Silent enroll with Server: {server_url}, Dept: {department}")
            from agent.installer.wizard import SentinelEnrollmentWizard
            wizard = SentinelEnrollmentWizard()
            wizard.server_url_var.set(server_url)
            wizard.token_var.set(token)
            wizard.department_var.set(department)
            wizard.execute_enrollment()
            return

        # 4. Agent Daemon Foreground Run Mode
        if first_arg == "run":
            logger.info("Running Agent daemon in foreground loop...")
            try:
                asyncio.run(async_service_start())
            except KeyboardInterrupt:
                if _stop_event:
                    _stop_event.set()
            return

        # 5. Windows SCM Actions (install, uninstall, start, stop)
        if first_arg in ("install", "start", "stop"):
            if os.name == "nt":
                import win32serviceutil
                from agent.services.service import SentinelAgentService
                sys.argv = [sys.argv[0], first_arg]
                win32serviceutil.HandleCommandLine(SentinelAgentService)

                if first_arg == "install":
                    try:
                        subprocess.run(
                            'sc.exe failure SentinelAgent reset= 86400 actions= restart/60000/restart/120000/restart/300000',
                            shell=True,
                            check=True
                        )
                    except Exception as e:
                        logger.warning(f"Failed to register service failure actions: {e}")
            else:
                logger.error("Windows SCM controls are only supported on Windows platform hosts.")
            return

        # 6. Fallback for any unknown argument -> Launch GUI Wizard
        logger.info(f"Argument '{first_arg}' passed. Launching GUI Enrollment Wizard...")
        from agent.installer.wizard import SentinelEnrollmentWizard
        wizard = SentinelEnrollmentWizard()
        wizard.run()

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        logger.critical(f"UNHANDLED EXCEPTION IN AGENT SETUP:\n{err_msg}")
        print(f"CRITICAL ERROR:\n{err_msg}", file=sys.stderr)
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\nCRITICAL TRACEBACK:\n{err_msg}\n")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    run_service_manager()
