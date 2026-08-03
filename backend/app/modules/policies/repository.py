from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.policies.models import Policy, PolicyVersion, PolicyAssignment, PolicyResult

class PolicyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, policy: Policy) -> Policy:
        self.session.add(policy)
        await self.session.commit()
        await self.session.refresh(policy)

        # Record initial version
        version = PolicyVersion(
            policy_id=policy.id,
            version=policy.version,
            settings=policy.settings,
            change_summary="Initial policy creation",
            created_by=policy.created_by
        )
        self.session.add(version)
        await self.session.commit()
        return policy

    async def get_by_id(self, policy_id: str) -> Optional[Policy]:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalars().first()

    async def list_policies(self, category: Optional[str] = None) -> List[Policy]:
        query = select(Policy)
        if category:
            query = query.where(Policy.category == category)
        result = await self.session.execute(query.order_by(Policy.updated_at.desc()))
        return list(result.scalars().all())

    async def update(self, policy: Policy, change_summary: Optional[str] = None) -> Policy:
        policy.version += 1
        await self.session.commit()

        # Add new version entry
        version = PolicyVersion(
            policy_id=policy.id,
            version=policy.version,
            settings=policy.settings,
            change_summary=change_summary or f"Updated to version {policy.version}",
            created_by=policy.created_by
        )
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def delete(self, policy_id: str) -> bool:
        policy = await self.get_by_id(policy_id)
        if not policy:
            return False
        await self.session.delete(policy)
        await self.session.commit()
        return True

    async def get_versions(self, policy_id: str) -> List[PolicyVersion]:
        result = await self.session.execute(
            select(PolicyVersion).where(PolicyVersion.policy_id == policy_id).order_by(PolicyVersion.version.desc())
        )
        return list(result.scalars().all())

    async def assign_policy(self, policy_id: str, target_type: str, target_ids: List[str], assigned_by: Optional[str] = None):
        for tid in target_ids:
            existing = await self.session.execute(
                select(PolicyAssignment).where(
                    PolicyAssignment.policy_id == policy_id,
                    PolicyAssignment.target_type == target_type,
                    PolicyAssignment.target_id == tid
                )
            )
            if not existing.scalars().first():
                assign = PolicyAssignment(
                    policy_id=policy_id,
                    target_type=target_type,
                    target_id=tid,
                    assigned_by=assigned_by
                )
                self.session.add(assign)
        await self.session.commit()
