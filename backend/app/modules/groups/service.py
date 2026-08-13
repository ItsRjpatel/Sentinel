from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.groups.repository import GroupRepository
from app.modules.groups.models import EndpointGroup
from app.modules.groups.schemas import (
    GroupCreate,
    GroupUpdate,
    GroupStats,
    GroupResponse,
)


class GroupService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GroupRepository(session)

    async def create_group(
        self, data: GroupCreate, user_name: Optional[str] = None
    ) -> GroupResponse:
        group = EndpointGroup(
            name=data.name,
            description=data.description,
            group_type=data.group_type,
            criteria=data.criteria,
            site=data.site,
            location=data.location,
            department=data.department,
            tags=data.tags,
            created_by=user_name,
        )
        created = await self.repo.create(group)
        if data.endpoint_ids:
            await self.repo.assign_endpoints(created.id, data.endpoint_ids, user_name)
        return await self.to_group_response(created)

    async def get_group(self, group_id: str) -> Optional[GroupResponse]:
        group = await self.repo.get_by_id(group_id)
        if not group:
            return None
        return await self.to_group_response(group)

    async def list_groups(self, search: Optional[str] = None) -> List[GroupResponse]:
        groups = await self.repo.list_groups(search)
        res = []
        for g in groups:
            res.append(await self.to_group_response(g))
        return res

    async def update_group(
        self, group_id: str, data: GroupUpdate
    ) -> Optional[GroupResponse]:
        group = await self.repo.get_by_id(group_id)
        if not group:
            return None
        if data.name is not None:
            group.name = data.name
        if data.description is not None:
            group.description = data.description
        if data.criteria is not None:
            group.criteria = data.criteria
        if data.site is not None:
            group.site = data.site
        if data.location is not None:
            group.location = data.location
        if data.department is not None:
            group.department = data.department
        if data.tags is not None:
            group.tags = data.tags

        updated = await self.repo.update(group)
        return await self.to_group_response(updated)

    async def delete_group(self, group_id: str) -> bool:
        return await self.repo.delete(group_id)

    async def assign_endpoints(
        self, group_id: str, endpoint_ids: List[str], user_name: Optional[str] = None
    ):
        await self.repo.assign_endpoints(group_id, endpoint_ids, user_name)

    async def remove_endpoint(self, group_id: str, endpoint_id: str):
        await self.repo.remove_endpoint(group_id, endpoint_id)

    async def get_group_endpoints(self, group_id: str):
        return await self.repo.get_group_endpoints(group_id)

    async def to_group_response(self, group: EndpointGroup) -> GroupResponse:
        endpoints = await self.repo.get_group_endpoints(group.id)
        total = len(endpoints)
        online = sum(
            1 for e in endpoints if getattr(e, "status", "") in ["healthy", "online"]
        )
        offline = total - online
        comp_percent = 100.0 if total == 0 else round((online / total) * 100.0, 1)
        health_percent = comp_percent

        stats = GroupStats(
            endpoint_count=total,
            online_count=online,
            offline_count=offline,
            compliance_percent=comp_percent,
            health_percent=health_percent,
        )

        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            group_type=group.group_type,
            criteria=group.criteria,
            site=group.site,
            location=group.location,
            department=group.department,
            tags=group.tags,
            created_by=group.created_by,
            created_at=group.created_at,
            updated_at=group.updated_at,
            stats=stats,
        )
