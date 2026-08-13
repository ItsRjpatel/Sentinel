from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.policies.schemas import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyVersionResponse,
    PolicyAssignRequest,
    PolicyConflictInfo,
)
from app.modules.policies.service import PolicyService

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.list_policies(category)


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    data: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.create_policy(data, current_user.username)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    data: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    updated = await service.update_policy(policy_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Policy not found")
    return updated


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    success = await service.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")


@router.get("/{policy_id}/versions", response_model=List[PolicyVersionResponse])
async def get_policy_versions(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.get_versions(policy_id)


@router.post("/{policy_id}/rollback/{version_number}", response_model=PolicyResponse)
async def rollback_policy(
    policy_id: str,
    version_number: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    rolled_back = await service.rollback(
        policy_id, version_number, current_user.username
    )
    if not rolled_back:
        raise HTTPException(
            status_code=400, detail="Rollback failed. Invalid version number or policy."
        )
    return rolled_back


@router.post("/{policy_id}/clone", response_model=PolicyResponse)
async def clone_policy(
    policy_id: str,
    new_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    cloned = await service.clone_policy(policy_id, new_name, current_user.username)
    if not cloned:
        raise HTTPException(status_code=404, detail="Policy not found")
    return cloned


@router.post("/{policy_id}/assign")
async def assign_policy(
    policy_id: str,
    payload: PolicyAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    await service.assign_policy(
        policy_id, payload.target_type, payload.target_ids, current_user.username
    )
    return {"message": f"Policy assigned to {len(payload.target_ids)} targets"}


@router.post("/check-conflicts", response_model=PolicyConflictInfo)
async def check_policy_conflicts(
    payload: PolicyAssignRequest,
    category: str = "Defender",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.check_conflicts(
        payload.target_type, payload.target_ids, category
    )
