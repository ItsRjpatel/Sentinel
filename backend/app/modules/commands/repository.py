from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.commands.models import Command
from app.modules.commands.enums import CommandStatus
from app.modules.endpoints.models import Endpoint

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

    async def create_bulk(self, commands: List[Command]) -> List[Command]:
        self.session.add_all(commands)
        await self.session.commit()
        for cmd in commands:
            await self.session.refresh(cmd)
        return commands

    async def get_by_id(self, command_id: UUID) -> Optional[Command]:
        stmt = select(Command).options(selectinload(Command.endpoint)).where(Command.id == command_id)
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
        now = get_utc_now()
        stmt = select(Command).where(
            Command.endpoint_id == endpoint_id,
            Command.status == CommandStatus.PENDING.value,
            or_(Command.scheduled_at == None, Command.scheduled_at <= now)
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
            command.started_at = command.completed_at
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
        stmt = select(Command).options(selectinload(Command.endpoint)).where(Command.endpoint_id == endpoint_id).order_by(Command.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_recent(self, skip: int = 0, limit: int = 100) -> List[Command]:
        stmt = select(Command).options(selectinload(Command.endpoint)).order_by(Command.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_commands_paginated(
        self,
        status_filter: Optional[str] = None,
        command_type: Optional[str] = None,
        endpoint_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Command], int]:
        stmt = select(Command).join(Endpoint, Command.endpoint_id == Endpoint.id, isouter=True).options(selectinload(Command.endpoint))
        count_stmt = select(func.count(Command.id)).join(Endpoint, Command.endpoint_id == Endpoint.id, isouter=True)

        filters = []
        if status_filter:
            if status_filter.upper() == "SCHEDULED":
                filters.append(and_(Command.status == CommandStatus.PENDING.value, Command.scheduled_at != None, Command.scheduled_at > get_utc_now()))
            else:
                filters.append(Command.status == status_filter.upper())
        
        if command_type:
            filters.append(Command.command_type == command_type.upper())

        if endpoint_id:
            filters.append(Command.endpoint_id == endpoint_id)

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Command.command_type.ilike(search_pattern),
                    Command.created_by.ilike(search_pattern),
                    Endpoint.hostname.ilike(search_pattern)
                )
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(Command.created_at.desc()).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        commands = list(res.scalars().all())

        return commands, total

    async def get_summary_counts(self) -> dict:
        now = get_utc_now()
        stmt = select(Command.status, Command.scheduled_at, func.count(Command.id)).group_by(Command.status, Command.scheduled_at)
        res = await self.session.execute(stmt)
        rows = res.all()

        counts = {
            "pending": 0,
            "running": 0,
            "success": 0,
            "failed": 0,
            "timed_out": 0,
            "cancelled": 0,
            "scheduled": 0,
            "total": 0
        }

        for status_val, sched_at, count in rows:
            counts["total"] += count
            st = (status_val or "").upper()
            if st in ["PENDING", "SENT"]:
                if sched_at and sched_at > now:
                    counts["scheduled"] += count
                else:
                    counts["pending"] += count
            elif st == "RUNNING":
                counts["running"] += count
            elif st in ["SUCCESS", "COMPLETED"]:
                counts["success"] += count
            elif st == "FAILED":
                counts["failed"] += count
            elif st == "TIMEOUT":
                counts["timed_out"] += count
            elif st == "CANCELLED":
                counts["cancelled"] += count

        return counts
