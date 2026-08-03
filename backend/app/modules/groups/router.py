from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.groups.schemas import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupBulkAssignRequest
)
from app.modules.groups.service import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("", response_model=List[GroupResponse])
async def list_groups(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    return await service.list_groups(search)

@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    return await service.create_group(data, current_user.username)

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    group = await service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    updated = await service.update_group(group_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    success = await service.delete_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")

@router.get("/{group_id}/endpoints")
async def get_group_endpoints(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    endpoints = await service.get_group_endpoints(group_id)
    return [
        {
            "id": e.id,
            "hostname": e.hostname,
            "os_version": e.os_version,
            "ip_address": e.ip_address,
            "status": e.status,
            "last_seen": e.last_seen
        }
        for e in endpoints
    ]

@router.post("/{group_id}/assign")
async def assign_endpoints_to_group(
    group_id: str,
    endpoint_ids: List[str],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    await service.assign_endpoints(group_id, endpoint_ids, current_user.username)
    return {"message": f"Assigned {len(endpoint_ids)} endpoints to group"}

@router.delete("/{group_id}/endpoints/{endpoint_id}")
async def remove_endpoint_from_group(
    group_id: str,
    endpoint_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    await service.remove_endpoint(group_id, endpoint_id)
    return {"message": "Endpoint removed from group"}

@router.post("/bulk-assign")
async def bulk_assign_groups(
    payload: GroupBulkAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = GroupService(db)
    for gid in payload.group_ids:
        await service.assign_endpoints(gid, payload.endpoint_ids, current_user.username)
    return {"message": "Bulk group assignment completed"}
