from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commands.repository import CommandRepository
from app.modules.commands.models import Command
from app.modules.commands.schemas import CommandCreate, CommandStatusUpdate
from app.modules.commands.enums import CommandStatus, CommandType
from app.modules.endpoints.models import Endpoint

class CommandService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CommandRepository(session)

    def _get_utc_now(self):
        return datetime.now(timezone.utc)

    async def queue_command(self, cmd_in: CommandCreate) -> Command:
        # 1. Validate endpoint exists
        stmt = select(Endpoint).where(Endpoint.id == cmd_in.endpoint_id)
        res = await self.session.execute(stmt)
        endpoint = res.scalar_one_or_none()
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Endpoint {cmd_in.endpoint_id} not found."
            )

        # 2. Prevent duplicate pending inventory commands
        if cmd_in.command_type == CommandType.RUN_INVENTORY:
            pending_commands = await self.repository.get_pending_for_endpoint(
                endpoint_id=cmd_in.endpoint_id, 
                command_type=CommandType.RUN_INVENTORY.value
            )
            if pending_commands:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A RUN_INVENTORY command is already pending for this endpoint."
                )

        # 3. Calculate expiration
        expires_at = None
        if cmd_in.expires_in_seconds:
            expires_at = self._get_utc_now() + timedelta(seconds=cmd_in.expires_in_seconds)

        command = Command(
            endpoint_id=cmd_in.endpoint_id,
            command_type=cmd_in.command_type.value,
            payload=cmd_in.payload,
            created_by=cmd_in.created_by,
            expires_at=expires_at,
            status=CommandStatus.PENDING.value
        )

        return await self.repository.create(command)

    async def get_command(self, command_id: UUID) -> Command:
        command = await self.repository.get_by_id(command_id)
        if not command:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Command not found."
            )
        return command

    async def cancel_command(self, command_id: UUID) -> Command:
        command = await self.get_command(command_id)
        if command.status != CommandStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel command in status {command.status}."
            )
        return await self.repository.mark_cancelled(command)

    async def poll_command(self, endpoint_id: UUID) -> Optional[Command]:
        # Validate endpoint exists
        stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
        res = await self.session.execute(stmt)
        endpoint = res.scalar_one_or_none()
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found."
            )

        command = await self.repository.get_oldest_pending_for_endpoint_and_lock(endpoint_id)
        if not command:
            return None

        # Expire old commands instead of sending them
        if command.expires_at and self._get_utc_now() > command.expires_at:
            await self.repository.mark_timeout(command)
            return None

        return await self.repository.mark_sent(command)

    async def get_endpoint_commands(self, endpoint_id: UUID, skip: int = 0, limit: int = 100) -> List[Command]:
        # Validate endpoint exists
        stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
        res = await self.session.execute(stmt)
        endpoint = res.scalar_one_or_none()
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found."
            )
        return await self.repository.list_by_endpoint(endpoint_id, skip=skip, limit=limit)

    async def update_command_result(self, command_id: UUID, success: bool, result: Optional[dict] = None, error_message: Optional[str] = None) -> Command:
        command = await self.get_command(command_id)
        if command.status not in [CommandStatus.SENT.value, CommandStatus.RUNNING.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update result for command in status {command.status}."
            )
        return await self.repository.update_result(
            command=command,
            success=success,
            result=result,
            error_message=error_message
        )
