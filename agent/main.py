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
        verify_tls=False  # Disabled verify for testing/internal domain certificates
    )

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

    # 7. Initialize Heartbeat Service and Scheduler Container
    container.heartbeat_service = HeartbeatTask(
        interval_seconds=config.heartbeat_interval_seconds,
        client=container.http_client,
        storage=container.storage,
        enrollment_manager=container.enrollment_service,
        config_version=config.config_version
    )

    container.scheduler = Scheduler()
    container.scheduler.register_task(container.heartbeat_service)

    # 8. Start Async Scheduler execution loop
    await container.scheduler.start()
    logger.info("Sentinel Agent successfully started.")

    # Block thread until stop signal is sent
    await _stop_event.wait()
    
    # Graceful cleanup
    logger.info("Shutting down Sentinel Agent service...")
    await container.scheduler.stop()
    await container.http_client.close()
    logger.info("Sentinel Agent shutdown completed.")


def run_service_manager() -> None:
    """Manages SCM CLI installation hooks and runs local console loops."""
    parser = argparse.ArgumentParser(description="Sentinel Windows Agent CLI Manager")
    parser.add_argument("action", choices=["install", "uninstall", "start", "stop", "run"], help="Action to execute")
    args = parser.parse_args()

    if args.action == "run":
        # Run agent in foreground console mode (development/manual debug runs)
        try:
            asyncio.run(async_service_start())
        except KeyboardInterrupt:
            if _stop_event:
                _stop_event.set()
    else:
        # standard Windows SCM controls
        if os.name == "nt":
            import win32serviceutil
            from agent.services.service import SentinelAgentService
            
            # Delegate SCM action
            sys.argv = [sys.argv[0], args.action]
            win32serviceutil.HandleCommandLine(SentinelAgentService)
            
            # Configure recovery actions programmatically after installation
            if args.action == "install":
                logger.info("Configuring Windows Service recovery failure actions...")
                try:
                    subprocess.run(
                        'sc.exe failure SentinelAgent reset= 86400 actions= restart/60000/restart/120000/restart/300000',
                        shell=True,
                        check=True
                    )
                    logger.info("SCM failure actions registered successfully.")
                except Exception as e:
                    logger.warning(f"Failed to register service failure actions: {e}")
        else:
            print("Windows SCM controls are only supported on Windows platform hosts.")
            sys.exit(1)


if __name__ == "__main__":
    run_service_manager()
