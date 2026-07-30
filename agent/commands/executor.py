import logging
import time
from typing import Dict, Any

from agent.commands.handlers import ping, inventory, processes, services

logger = logging.getLogger(__name__)

class CommandExecutor:
    """Executes backend commands in an isolated scope."""

    def __init__(self):
        self.handlers = {
            "PING": ping.execute,
            "RUN_INVENTORY": inventory.execute,
            "GET_PROCESS_LIST": processes.execute,
            "RESTART_SERVICE": services.handle_restart_service,
            "GET_SERVICE_LIST": services.handle_get_service_list,
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
            result["success"] = handler_result.get("success", True) if isinstance(handler_result, dict) else True
            result["result"] = handler_result
            
        except Exception as e:
            logger.error(f"Command failed: {command_id} - {e}")
            result["error"] = str(e)
            result["success"] = False
            
        duration_ms = int((time.time() - start_time) * 1000)
        result["duration_ms"] = duration_ms
        
        logger.info(f"Command completed: {command_id} ({command_type}) in {duration_ms}ms, Success: {result['success']}")
        
        return result
