from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.commands.models import Command
from app.modules.commands.enums import CommandStatus

def get_utc_now():
    return datetime.now(timezone.utc)

class CommandRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, command: Command) -> Command:
        self.session.add(command)
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def get_by_id(self, command_id: UUID) -> Optional[Command]:
        stmt = select(Command).where(Command.id == command_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_pending_for_endpoint(self, endpoint_id: UUID, command_type: str = None) -> List[Command]:
        stmt = select(Command).where(
            Command.endpoint_id == endpoint_id,
            Command.status == CommandStatus.PENDING.value
        )
        if command_type:
            stmt = stmt.where(Command.command_type == command_type)
        stmt = stmt.order_by(Command.created_at.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_oldest_pending_for_endpoint_and_lock(self, endpoint_id: UUID) -> Optional[Command]:
        stmt = select(Command).where(
            Command.endpoint_id == endpoint_id,
            Command.status == CommandStatus.PENDING.value
        ).order_by(Command.created_at.asc()).with_for_update(skip_locked=True).limit(1)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def mark_sent(self, command: Command) -> Command:
        command.status = CommandStatus.SENT.value
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def mark_running(self, command: Command) -> Command:
        command.status = CommandStatus.RUNNING.value
        command.started_at = get_utc_now()
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def mark_success(self, command: Command, result: dict = None) -> Command:
        command.status = CommandStatus.SUCCESS.value
        command.completed_at = get_utc_now()
        if result:
            command.result = result
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def update_result(self, command: Command, success: bool, result: dict = None, error_message: str = None) -> Command:
        command.status = CommandStatus.SUCCESS.value if success else CommandStatus.FAILED.value
        command.completed_at = get_utc_now()
        if not command.started_at:
            command.started_at = command.completed_at # fallback if not marked running
        if result is not None:
            command.result = result
        if error_message is not None:
            command.error_message = error_message
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def mark_failed(self, command: Command, error_message: str = None) -> Command:
        command.status = CommandStatus.FAILED.value
        command.completed_at = get_utc_now()
        if error_message:
            command.error_message = error_message
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def mark_timeout(self, command: Command) -> Command:
        command.status = CommandStatus.TIMEOUT.value
        command.completed_at = get_utc_now()
        await self.session.commit()
        await self.session.refresh(command)
        return command
        
    async def mark_cancelled(self, command: Command) -> Command:
        command.status = CommandStatus.CANCELLED.value
        command.completed_at = get_utc_now()
        await self.session.commit()
        await self.session.refresh(command)
        return command

    async def list_by_endpoint(self, endpoint_id: UUID, skip: int = 0, limit: int = 100) -> List[Command]:
        stmt = select(Command).where(Command.endpoint_id == endpoint_id).order_by(Command.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_recent(self, skip: int = 0, limit: int = 100) -> List[Command]:
        stmt = select(Command).order_by(Command.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
