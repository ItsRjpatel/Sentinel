from typing import List, Optional, Tuple
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.groups.models import EndpointGroup, EndpointGroupMember
from app.modules.endpoints.models import Endpoint

class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, group: EndpointGroup) -> EndpointGroup:
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group

    async def get_by_id(self, group_id: str) -> Optional[EndpointGroup]:
        result = await self.session.execute(
            select(EndpointGroup).options(selectinload(EndpointGroup.members)).where(EndpointGroup.id == group_id)
        )
        return result.scalars().first()

    async def list_groups(self, search: Optional[str] = None) -> List[EndpointGroup]:
        query = select(EndpointGroup).options(selectinload(EndpointGroup.members))
        if search:
            query = query.where(EndpointGroup.name.ilike(f"%{search}%"))
        result = await self.session.execute(query.order_by(EndpointGroup.name))
        return list(result.scalars().all())

    async def update(self, group: EndpointGroup) -> EndpointGroup:
        await self.session.commit()
        await self.session.refresh(group)
        return group

    async def delete(self, group_id: str) -> bool:
        group = await self.get_by_id(group_id)
        if not group:
            return False
        await self.session.delete(group)
        await self.session.commit()
        return True

    async def assign_endpoints(self, group_id: str, endpoint_ids: List[str], assigned_by: Optional[str] = None):
        for ep_id in endpoint_ids:
            existing = await self.session.execute(
                select(EndpointGroupMember).where(
                    EndpointGroupMember.group_id == group_id,
                    EndpointGroupMember.endpoint_id == ep_id
                )
            )
            if not existing.scalars().first():
                member = EndpointGroupMember(
                    group_id=group_id,
                    endpoint_id=ep_id,
                    assigned_by=assigned_by
                )
                self.session.add(member)
        await self.session.commit()

    async def remove_endpoint(self, group_id: str, endpoint_id: str):
        await self.session.execute(
            delete(EndpointGroupMember).where(
                EndpointGroupMember.group_id == group_id,
                EndpointGroupMember.endpoint_id == endpoint_id
            )
        )
        await self.session.commit()

    async def get_group_endpoints(self, group_id: str) -> List[Endpoint]:
        result = await self.session.execute(
            select(Endpoint)
            .join(EndpointGroupMember, EndpointGroupMember.endpoint_id == Endpoint.id)
            .where(EndpointGroupMember.group_id == group_id)
        )
        return list(result.scalars().all())
