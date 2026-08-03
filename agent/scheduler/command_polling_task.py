import logging
import asyncio

from agent.scheduler.scheduler import ScheduledTask
from agent.communication.client import AgentHTTPClient

logger = logging.getLogger(__name__)

class CommandPollingTask(ScheduledTask):
    """
    Polls the backend for pending commands and acknowledges receipt.
    Does NOT execute commands yet.
    """

    def __init__(self, backend_client: AgentHTTPClient, interval_seconds: int = 10):
        super().__init__(interval_seconds)
        self.backend_client = backend_client
        
        # Instantiate executor inline to avoid circular imports if any, or just import it at top.
        from agent.commands.executor import CommandExecutor
        self.executor = CommandExecutor()

    async def execute(self):
        logger.info("[STAGE 1: POLL] Polling backend for pending commands...")
        try:
            command = await self.backend_client.poll_command()
            if not command:
                logger.info("[STAGE 1: POLL] No pending commands available.")
            else:
                cmd_id = command.get("id") or command.get("command_id")
                cmd_type = command.get("command_type")
                logger.info(f"[STAGE 2: RECEIVE] Command received from backend | ID: {cmd_id} | Type: {cmd_type}")
                
                # Execute the command
                try:
                    logger.info(f"[STAGE 3: EXECUTE] Executing command {cmd_id} ({cmd_type})...")
                    result = self.executor.execute(command)
                    logger.info(f"[STAGE 3: EXECUTE] Execution finished for {cmd_id} | Success: {result.get('success')}")
                    
                    # Extract result payload cleanly
                    res_payload = result.get("result") if "result" in result else {k: v for k, v in result.items() if k not in ["success", "duration_ms", "error"]}
                    err_msg = result.get("error") or result.get("error_message") or result.get("stderr")
                    
                    logger.info(f"[STAGE 4: UPLOAD RESULT] Uploading command result for {cmd_id}...")
                    uploaded = await self.backend_client.upload_command_result(
                        command_id=cmd_id,
                        success=result.get("success", False),
                        duration_ms=result.get("duration_ms"),
                        result=res_payload,
                        error=err_msg
                    )
                    if uploaded:
                        logger.info(f"[STAGE 4: UPLOAD RESULT] Command {cmd_id} result uploaded successfully.")
                    else:
                        logger.error(f"[STAGE 4: UPLOAD RESULT] Failed to upload command result for {cmd_id}.")
                except Exception as ex:
                    logger.error(f"Error during command execution wrapper for {cmd_id}: {ex}")
        except Exception as e:
            logger.error(f"Failed to poll for commands: {e}")
