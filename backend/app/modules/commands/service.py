from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commands.repository import CommandRepository
from app.modules.commands.models import Command
from app.modules.commands.schemas import CommandCreate, BulkCommandCreate, BulkCommandResponse
from app.modules.commands.enums import CommandStatus, CommandType
from app.modules.endpoints.models import Endpoint
from app.core.events.dispatcher import event_dispatcher

import logging

logger = logging.getLogger(__name__)

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
            scheduled_at=cmd_in.scheduled_at,
            recurring=cmd_in.recurring,
            timezone=cmd_in.timezone,
            status=CommandStatus.PENDING.value
        )

        created_cmd = await self.repository.create(command)
        logger.info(f"[COMMAND LIFECYCLE: QUEUED] Command {created_cmd.id} queued for Endpoint {created_cmd.endpoint_id} ({created_cmd.command_type})")
        
        event_dispatcher.publish("COMMAND_QUEUED", {
            "id": str(created_cmd.id),
            "endpoint_id": str(created_cmd.endpoint_id),
            "command_type": created_cmd.command_type,
            "status": created_cmd.status,
            "payload": created_cmd.payload,
            "created_by": created_cmd.created_by
        })
        
        return created_cmd

    async def queue_bulk_commands(self, bulk_in: BulkCommandCreate, created_by: str) -> BulkCommandResponse:
        if not bulk_in.endpoint_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one endpoint must be specified.")

        created_commands = []
        expires_at = None
        if bulk_in.expires_in_seconds:
            expires_at = self._get_utc_now() + timedelta(seconds=bulk_in.expires_in_seconds)

        for ep_id in bulk_in.endpoint_ids:
            cmd = Command(
                endpoint_id=ep_id,
                command_type=bulk_in.command_type.value,
                payload=bulk_in.payload,
                created_by=created_by,
                expires_at=expires_at,
                scheduled_at=bulk_in.scheduled_at,
                timezone=bulk_in.timezone,
                status=CommandStatus.PENDING.value
            )
            created_commands.append(cmd)

        saved_commands = await self.repository.create_bulk(created_commands)

        for c in saved_commands:
            logger.info(f"[COMMAND LIFECYCLE: BULK QUEUED] Command {c.id} queued for Endpoint {c.endpoint_id} ({c.command_type})")
            event_dispatcher.publish("COMMAND_QUEUED", {
                "id": str(c.id),
                "endpoint_id": str(c.endpoint_id),
                "command_type": c.command_type,
                "status": c.status,
                "payload": c.payload,
                "created_by": c.created_by
            })

        return BulkCommandResponse(
            queued_count=len(saved_commands),
            command_ids=[c.id for c in saved_commands]
        )

    async def retry_command(self, command_id: UUID, created_by: str) -> Command:
        original = await self.get_command(command_id)
        if original.status.upper() not in [CommandStatus.FAILED.value, CommandStatus.TIMEOUT.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only retry commands in FAILED or TIMEOUT status, not {original.status}."
            )

        new_cmd_in = CommandCreate(
            endpoint_id=original.endpoint_id,
            command_type=CommandType(original.command_type),
            payload=original.payload,
            created_by=created_by,
            expires_in_seconds=3600
        )
        new_cmd = await self.queue_command(new_cmd_in)
        new_cmd.retry_count = original.retry_count + 1
        await self.session.commit()
        await self.session.refresh(new_cmd)
        logger.info(f"[COMMAND LIFECYCLE: RETRIED] Retried Command {original.id} -> New Command {new_cmd.id}")
        return new_cmd

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
        if command.status.upper() != CommandStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel command in status {command.status}."
            )
        cancelled = await self.repository.mark_cancelled(command)
        logger.info(f"[COMMAND LIFECYCLE: CANCELLED] Command {cancelled.id} marked CANCELLED")
        
        event_dispatcher.publish("COMMAND_CANCELLED", {
            "id": str(cancelled.id),
            "endpoint_id": str(cancelled.endpoint_id),
            "command_type": cancelled.command_type,
            "status": cancelled.status
        })
        return cancelled

    async def poll_command(self, endpoint_id: UUID) -> Optional[Command]:
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

        if command.expires_at and self._get_utc_now() > command.expires_at:
            timed_out = await self.repository.mark_timeout(command)
            logger.warning(f"[COMMAND LIFECYCLE: TIMEOUT] Command {timed_out.id} expired prior to poll")
            event_dispatcher.publish("COMMAND_TIMEOUT", {
                "id": str(timed_out.id),
                "endpoint_id": str(timed_out.endpoint_id),
                "command_type": timed_out.command_type,
                "status": timed_out.status
            })
            return None

        sent_cmd = await self.repository.mark_sent(command)
        logger.info(f"[COMMAND LIFECYCLE: SENT] Command {sent_cmd.id} ({sent_cmd.command_type}) sent to Endpoint {endpoint_id}")
        
        event_dispatcher.publish("COMMAND_SENT", {
            "id": str(sent_cmd.id),
            "endpoint_id": str(sent_cmd.endpoint_id),
            "command_type": sent_cmd.command_type,
            "status": sent_cmd.status,
            "payload": sent_cmd.payload,
            "created_by": sent_cmd.created_by
        })
        
        return sent_cmd

    async def get_endpoint_commands(self, endpoint_id: UUID, skip: int = 0, limit: int = 100) -> List[Command]:
        stmt = select(Endpoint).where(Endpoint.id == endpoint_id)
        res = await self.session.execute(stmt)
        endpoint = res.scalar_one_or_none()
        if not endpoint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endpoint not found."
            )
        return await self.repository.list_by_endpoint(endpoint_id, skip=skip, limit=limit)

    async def list_commands_paginated(
        self,
        status_filter: Optional[str] = None,
        command_type: Optional[str] = None,
        endpoint_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Command], int]:
        skip = (page - 1) * page_size
        return await self.repository.list_commands_paginated(
            status_filter=status_filter,
            command_type=command_type,
            endpoint_id=endpoint_id,
            search=search,
            skip=skip,
            limit=page_size
        )

    async def get_summary_counts(self) -> dict:
        return await self.repository.get_summary_counts()

    async def update_command_result(self, command_id: UUID, success: bool, result: Optional[dict] = None, error_message: Optional[str] = None) -> Command:
        command = await self.get_command(command_id)
        valid_statuses = [CommandStatus.SENT.value, CommandStatus.RUNNING.value, "sent", "running"]
        if command.status.upper() not in [s.upper() for s in valid_statuses]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update result for command in status {command.status}."
            )
        updated_cmd = await self.repository.update_result(
            command=command,
            success=success,
            result=result,
            error_message=error_message
        )
        logger.info(f"[COMMAND LIFECYCLE: {updated_cmd.status}] Command {command_id} result uploaded: Success={success}")
        
        event_dispatcher.publish(f"COMMAND_{updated_cmd.status}", {
            "id": str(updated_cmd.id),
            "endpoint_id": str(updated_cmd.endpoint_id),
            "command_type": updated_cmd.command_type,
            "status": updated_cmd.status,
            "result": updated_cmd.result,
            "error_message": updated_cmd.error_message
        })
        
        return updated_cmd
