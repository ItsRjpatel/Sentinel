import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, oauth2_scheme
from app.core.security import verify_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.schemas import HardwareInventoryCreate, HardwareInventoryResponse
from app.modules.inventory.repository import HardwareInventoryRepository
from app.modules.inventory.service import HardwareInventoryService

router = APIRouter(tags=["inventory"])

def get_inventory_repository(session: AsyncSession = Depends(get_db)) -> HardwareInventoryRepository:
    return HardwareInventoryRepository(session)

def get_inventory_service(
    session: AsyncSession = Depends(get_db),
    repo: HardwareInventoryRepository = Depends(get_inventory_repository)
) -> HardwareInventoryService:
    return HardwareInventoryService(session, repo)


async def _resolve_authenticated_endpoint(token: str, db: AsyncSession) -> uuid.UUID:
    """Helper method decodes JWT credentials and asserts registered endpoint existence."""
    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {e}")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Missing subject parameter in session.")

    try:
        agent_id = uuid.UUID(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed session credentials.")

    # Confirm the endpoint is enrolled
    stmt = select(Endpoint).where(Endpoint.id == agent_id)
    res = await db.execute(stmt)
    endpoint = res.scalar_one_or_none()
    if not endpoint:
         raise HTTPException(status_code=401, detail="Endpoint record not registered.")

    return agent_id


@router.post("/inventory/hardware", response_model=SuccessResponse[HardwareInventoryResponse])
async def upload_hardware(
    data: HardwareInventoryCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: HardwareInventoryService = Depends(get_inventory_service)
):
    """Enrolled Windows Agents submit collected hardware telemetry payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    record = await service.save_hardware_inventory(agent_id, data)
    return SuccessResponse(
        message="Hardware inventory uploaded successfully",
        data=HardwareInventoryResponse.model_validate(record)
    )


@router.get("/inventory/hardware", response_model=SuccessResponse[HardwareInventoryResponse])
async def get_my_hardware(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: HardwareInventoryService = Depends(get_inventory_service)
):
    """Retrieve the hardware specifications linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    record = await service.get_hardware_inventory(agent_id)
    if not record:
        raise HTTPException(status_code=404, detail="No hardware inventory record found.")
    return SuccessResponse(
        message="Hardware inventory retrieved",
        data=HardwareInventoryResponse.model_validate(record)
    )


@router.get("/inventory/{endpoint_id}", response_model=SuccessResponse[HardwareInventoryResponse])
async def get_endpoint_hardware(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: HardwareInventoryService = Depends(get_inventory_service)
):
    """Queries details of custom hardware metrics via target Endpoint UUID identifiers."""
    # Authenticate token exists
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    record = await service.get_hardware_inventory(endpoint_id)
    if not record:
        raise HTTPException(status_code=404, detail="No inventory record matched for target ID.")
    return SuccessResponse(
        message="Hardware inventory retrieved",
        data=HardwareInventoryResponse.model_validate(record)
    )
