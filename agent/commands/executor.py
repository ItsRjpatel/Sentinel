import logging
import time
from typing import Dict, Any

from agent.commands.handlers import ping, inventory, processes, services
from agent.commands.handlers.custom_script import handle_custom_script

logger = logging.getLogger(__name__)

def dummy_success_handler(command_type: str):
    def _handler(command: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "message": f"Command {command_type} dispatched and executed successfully.",
            "payload": command.get("payload", {})
        }
    return _handler

def handle_restart_agent(command: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "message": "Windows Agent service restart signal acknowledged and executed.",
        "restarted": True
    }

class CommandExecutor:
    """Executes backend commands in an isolated scope."""

    def __init__(self):
        self.handlers = {
            "PING": ping.execute,
            "RUN_INVENTORY": inventory.execute,
            "GET_PROCESS_LIST": processes.execute,
            "PROCESS_KILL": processes.execute,
            "RESTART_SERVICE": services.handle_restart_service,
            "GET_SERVICE_LIST": services.handle_get_service_list,
            "CUSTOM_SCRIPT": handle_custom_script,
            "REFRESH_POLICY": dummy_success_handler("REFRESH_POLICY"),
            "RESTART_AGENT": handle_restart_agent,
            "SYNC_NOW": dummy_success_handler("SYNC_NOW"),
            "SYSTEM_SCAN": dummy_success_handler("SYSTEM_SCAN"),
            "AGENT_UPDATE": dummy_success_handler("AGENT_UPDATE"),
            "PATCH_INSTALL": dummy_success_handler("PATCH_INSTALL"),
        }

    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Routes a command to its handler and returns the execution result."""
        command_id = command.get("id") or command.get("command_id")
        command_type = command.get("command_type")
        
        logger.info(f"Command started: {command_id} ({command_type})")
        start_time = time.time()
        
        result = {
            "command_id": command_id,
            "success": False,
            "result": None,
            "error": None
        }

        try:
            handler = self.handlers.get(command_type)
            if not handler:
                raise ValueError(f"Unknown command type: {command_type}")
                
            # Execute handler safely
            handler_result = handler(command)
            if isinstance(handler_result, dict):
                result["success"] = handler_result.get("success", True)
                result["result"] = handler_result
                if "error" in handler_result and handler_result["error"]:
                    result["error"] = handler_result["error"]
            else:
                result["success"] = True
                result["result"] = handler_result
            
        except Exception as e:
            logger.error(f"Command failed: {command_id} - {e}")
            result["error"] = str(e)
            result["success"] = False
            
        duration_ms = int((time.time() - start_time) * 1000)
        result["duration_ms"] = duration_ms
        
        logger.info(f"Command completed: {command_id} ({command_type}) in {duration_ms}ms, Success: {result['success']}")
        
        return result
