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
        logger.info("Polling for commands...")
        try:
            command = await self.backend_client.poll_command()
            if not command:
                logger.info("No commands available.")
            else:
                cmd_id = command.get("id") or command.get("command_id")
                cmd_type = command.get("command_type")
                logger.info(f"Command received:\nID: {cmd_id}\nType: {cmd_type}")
                
                # Execute the command
                try:
                    result = self.executor.execute(command)
                    logger.info(f"Command execution result: {result}")
                    
                    # Upload result
                    await self.backend_client.upload_command_result(
                        command_id=cmd_id,
                        success=result.get("success", False),
                        duration_ms=result.get("duration_ms"),
                        result=result.get("result"),
                        error=result.get("error")
                    )
                except Exception as ex:
                    logger.error(f"Error during command execution wrapper: {ex}")
        except Exception as e:
            logger.error(f"Failed to poll for commands: {e}")
