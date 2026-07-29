import sys
import os
import socket
import logging

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager

    class SentinelAgentService(win32serviceutil.ServiceFramework):
        """Native Windows Service wrapper for the Sentinel Windows Agent."""
        
        _svc_name_ = "SentinelAgent"
        _svc_display_name_ = "Sentinel Endpoint Management Agent"
        _svc_description_ = "Sentinel background daemon managing secure endpoint trust, heartbeats, and updates."

        def __init__(self, args: list) -> None:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            socket.setdefaulttimeout(60)
            self.is_running = True

        def SvcStop(self) -> None:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.is_running = False

        def SvcDoStart(self) -> None:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, "")
            )
            self.main()

        def main(self) -> None:
            import asyncio
            import threading
            
            # Create a dedicated async loop for the worker thread
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
            self.thread.start()

            # Block the SCM service controller thread until SvcStop signals self.hWaitStop
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

            # Signal async loop to shut down gracefully
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=10)

        def _run_async_loop(self) -> None:
            asyncio.set_event_loop(self.loop)
            from agent.main import async_service_start
            try:
                self.loop.run_until_complete(async_service_start())
            except Exception as e:
                # Log critical service crash
                logging.getLogger().critical(f"Agent service crashed: {e}", exc_info=True)
else:
    # Cross-platform mock service base class for test runs on non-Windows developer systems
    class SentinelAgentService:
        _svc_name_ = "SentinelAgent"
        
        def __init__(self, args: list) -> None:
            pass
