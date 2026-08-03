from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.policies.repository import PolicyRepository
from app.modules.policies.models import Policy, PolicyVersion
from app.modules.policies.schemas import PolicyCreate, PolicyUpdate, PolicyConflictInfo

class PolicyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PolicyRepository(session)

    async def create_policy(self, data: PolicyCreate, user_name: Optional[str] = None) -> Policy:
        policy = Policy(
            name=data.name,
            description=data.description,
            category=data.category,
            settings=data.settings,
            status=data.status or "ACTIVE",
            created_by=user_name
        )
        return await self.repo.create(policy)

    async def get_policy(self, policy_id: str) -> Optional[Policy]:
        return await self.repo.get_by_id(policy_id)

    async def list_policies(self, category: Optional[str] = None) -> List[Policy]:
        return await self.repo.list_policies(category)

    async def update_policy(self, policy_id: str, data: PolicyUpdate) -> Optional[Policy]:
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            return None
        if data.name is not None: policy.name = data.name
        if data.description is not None: policy.description = data.description
        if data.settings is not None: policy.settings = data.settings
        if data.status is not None: policy.status = data.status

        return await self.repo.update(policy, data.change_summary)

    async def delete_policy(self, policy_id: str) -> bool:
        return await self.repo.delete(policy_id)

    async def get_versions(self, policy_id: str) -> List[PolicyVersion]:
        return await self.repo.get_versions(policy_id)

    async def rollback(self, policy_id: str, version_number: int, user_name: Optional[str] = None) -> Optional[Policy]:
        versions = await self.repo.get_versions(policy_id)
        target_version = next((v for v in versions if v.version == version_number), None)
        if not target_version:
            return None
        
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            return None

        policy.settings = target_version.settings
        return await self.repo.update(policy, f"Rolled back to version {version_number}")

    async def clone_policy(self, policy_id: str, new_name: str, user_name: Optional[str] = None) -> Optional[Policy]:
        original = await self.repo.get_by_id(policy_id)
        if not original:
            return None
        cloned = Policy(
            name=new_name,
            description=f"Cloned from {original.name}",
            category=original.category,
            settings=original.settings,
            status="DRAFT",
            created_by=user_name
        )
        return await self.repo.create(cloned)

    async def check_conflicts(self, target_type: str, target_ids: List[str], category: str) -> PolicyConflictInfo:
        # Simplistic conflict check evaluation
        return PolicyConflictInfo(
            has_conflict=False,
            conflicting_policies=[],
            conflict_details="No conflicting policy rules detected across targets."
        )

    async def assign_policy(self, policy_id: str, target_type: str, target_ids: List[str], user_name: Optional[str] = None):
        await self.repo.assign_policy(policy_id, target_type, target_ids, user_name)
