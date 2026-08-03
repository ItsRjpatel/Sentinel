import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, oauth2_scheme
from app.core.security import verify_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.schemas import (
    HardwareInventoryCreate,
    HardwareInventoryResponse,
    OperatingSystemInventoryCreate,
    OperatingSystemInventoryResponse,
    NetworkAdapterInventoryCreate,
    NetworkAdapterInventoryResponse,
    PhysicalDiskInventoryCreate,
    PhysicalDiskInventoryResponse,
    SoftwareInventoryCreate,
    SoftwareInventoryResponse,
    WindowsUpdateInventoryCreate,
    WindowsUpdateInventoryResponse,
    WindowsServiceInventoryCreate,
    WindowsServiceInventoryResponse
)
from app.modules.inventory.repository import HardwareInventoryRepository, OperatingSystemInventoryRepository, NetworkAdapterInventoryRepository, StorageInventoryRepository, SoftwareInventoryRepository, WindowsUpdateInventoryRepository, WindowsServiceInventoryRepository
from app.modules.inventory.service import HardwareInventoryService, OperatingSystemInventoryService, NetworkAdapterInventoryService, StorageInventoryService, SoftwareInventoryService, WindowsUpdateInventoryService, WindowsServiceInventoryService

router = APIRouter(tags=["inventory"])

def get_inventory_repository(session: AsyncSession = Depends(get_db)) -> HardwareInventoryRepository:
    return HardwareInventoryRepository(session)

def get_inventory_service(
    session: AsyncSession = Depends(get_db),
    repo: HardwareInventoryRepository = Depends(get_inventory_repository)
) -> HardwareInventoryService:
    return HardwareInventoryService(session, repo)

def get_os_repository(session: AsyncSession = Depends(get_db)) -> OperatingSystemInventoryRepository:
    return OperatingSystemInventoryRepository(session)

def get_os_service(
    session: AsyncSession = Depends(get_db),
    repo: OperatingSystemInventoryRepository = Depends(get_os_repository)
) -> OperatingSystemInventoryService:
    return OperatingSystemInventoryService(session, repo)

def get_network_repository(session: AsyncSession = Depends(get_db)) -> NetworkAdapterInventoryRepository:
    return NetworkAdapterInventoryRepository(session)

def get_network_service(
    session: AsyncSession = Depends(get_db),
    repo: NetworkAdapterInventoryRepository = Depends(get_network_repository)
) -> NetworkAdapterInventoryService:
    return NetworkAdapterInventoryService(session, repo)

def get_storage_repository(session: AsyncSession = Depends(get_db)) -> StorageInventoryRepository:
    return StorageInventoryRepository(session)

def get_storage_service(
    session: AsyncSession = Depends(get_db),
    repo: StorageInventoryRepository = Depends(get_storage_repository)
) -> StorageInventoryService:
    return StorageInventoryService(session, repo)

def get_software_repository(session: AsyncSession = Depends(get_db)) -> SoftwareInventoryRepository:
    return SoftwareInventoryRepository(session)

def get_software_service(
    session: AsyncSession = Depends(get_db),
    repo: SoftwareInventoryRepository = Depends(get_software_repository)
) -> SoftwareInventoryService:
    return SoftwareInventoryService(session, repo)

def get_windows_update_repository(session: AsyncSession = Depends(get_db)) -> WindowsUpdateInventoryRepository:
    return WindowsUpdateInventoryRepository(session)

def get_windows_update_service(
    session: AsyncSession = Depends(get_db),
    repo: WindowsUpdateInventoryRepository = Depends(get_windows_update_repository)
) -> WindowsUpdateInventoryService:
    return WindowsUpdateInventoryService(session, repo)

def get_windows_service_repository(session: AsyncSession = Depends(get_db)) -> WindowsServiceInventoryRepository:
    return WindowsServiceInventoryRepository(session)

def get_windows_service_service(
    session: AsyncSession = Depends(get_db),
    repo: WindowsServiceInventoryRepository = Depends(get_windows_service_repository)
) -> WindowsServiceInventoryService:
    return WindowsServiceInventoryService(session, repo)


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



@router.post("/inventory/os", response_model=SuccessResponse[OperatingSystemInventoryResponse])
async def upload_os(
    data: OperatingSystemInventoryCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: OperatingSystemInventoryService = Depends(get_os_service)
):
    """Enrolled Windows Agents submit collected Operating System telemetry payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    record = await service.save_os_inventory(agent_id, data)
    return SuccessResponse(
        message="OS inventory uploaded successfully",
        data=OperatingSystemInventoryResponse.model_validate(record)
    )


@router.get("/inventory/os", response_model=SuccessResponse[OperatingSystemInventoryResponse])
async def get_my_os(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: OperatingSystemInventoryService = Depends(get_os_service)
):
    """Retrieve the operating system specifications linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    record = await service.get_os_inventory(agent_id)
    if not record:
        raise HTTPException(status_code=404, detail="No OS inventory record found.")
    return SuccessResponse(
        message="OS inventory retrieved",
        data=OperatingSystemInventoryResponse.model_validate(record)
    )


@router.get("/inventory/os/{endpoint_id}", response_model=SuccessResponse[OperatingSystemInventoryResponse])
async def get_endpoint_os(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: OperatingSystemInventoryService = Depends(get_os_service)
):
    """Queries details of custom operating system metrics via target Endpoint UUID identifiers."""
    # Authenticate token exists
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    record = await service.get_os_inventory(endpoint_id)
    if not record:
        raise HTTPException(status_code=404, detail="No inventory record matched for target ID.")
    return SuccessResponse(
        message="OS inventory retrieved",
        data=OperatingSystemInventoryResponse.model_validate(record)
    )


@router.post("/inventory/network", response_model=SuccessResponse[list[NetworkAdapterInventoryResponse]])
async def upload_network(
    data: list[NetworkAdapterInventoryCreate],
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: NetworkAdapterInventoryService = Depends(get_network_service)
):
    """Enrolled Windows Agents submit collected network adapter telemetry payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.save_network_inventory(agent_id, data)
    return SuccessResponse(
        message="Network inventory uploaded successfully",
        data=[NetworkAdapterInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/network", response_model=SuccessResponse[list[NetworkAdapterInventoryResponse]])
async def get_my_network(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: NetworkAdapterInventoryService = Depends(get_network_service)
):
    """Retrieve the network adapter specifications linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.get_network_inventory(agent_id)
    return SuccessResponse(
        message="Network inventory retrieved",
        data=[NetworkAdapterInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/network/{endpoint_id}", response_model=SuccessResponse[list[NetworkAdapterInventoryResponse]])
async def get_endpoint_network(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: NetworkAdapterInventoryService = Depends(get_network_service)
):
    """Queries details of custom network adapter metrics via target Endpoint UUID identifiers."""
    # Authenticate token exists
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    records = await service.get_network_inventory(endpoint_id)
    return SuccessResponse(
        message="Network inventory retrieved",
        data=[NetworkAdapterInventoryResponse.model_validate(r) for r in records]
    )


@router.post("/inventory/storage", response_model=SuccessResponse[list[PhysicalDiskInventoryResponse]])
async def upload_storage(
    data: list[PhysicalDiskInventoryCreate],
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: StorageInventoryService = Depends(get_storage_service)
):
    """Enrolled Windows Agents submit collected physical disk and volume telemetry payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.save_storage_inventory(agent_id, data)
    return SuccessResponse(
        message="Storage inventory uploaded successfully",
        data=[PhysicalDiskInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/storage", response_model=SuccessResponse[list[PhysicalDiskInventoryResponse]])
async def get_my_storage(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: StorageInventoryService = Depends(get_storage_service)
):
    """Retrieve the storage inventory linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.get_storage_inventory(agent_id)
    return SuccessResponse(
        message="Storage inventory retrieved",
        data=[PhysicalDiskInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/storage/{endpoint_id}", response_model=SuccessResponse[list[PhysicalDiskInventoryResponse]])
async def get_endpoint_storage(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: StorageInventoryService = Depends(get_storage_service)
):
    """Queries details of custom storage metrics via target Endpoint UUID identifiers."""
    # Authenticate token exists
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    records = await service.get_storage_inventory(endpoint_id)
    return SuccessResponse(
        message="Storage inventory retrieved",
        data=[PhysicalDiskInventoryResponse.model_validate(r) for r in records]
    )


@router.post("/inventory/software", response_model=SuccessResponse[list[SoftwareInventoryResponse]])
async def upload_software(
    data: list[SoftwareInventoryCreate],
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: SoftwareInventoryService = Depends(get_software_service)
):
    """Enrolled Windows Agents submit collected installed software telemetry payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.save_software_inventory(agent_id, data)
    return SuccessResponse(
        message="Software inventory uploaded successfully",
        data=[SoftwareInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/software", response_model=SuccessResponse[list[SoftwareInventoryResponse]])
async def get_my_software(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: SoftwareInventoryService = Depends(get_software_service)
):
    """Retrieve the installed software inventory linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.get_software_inventory(agent_id)
    return SuccessResponse(
        message="Software inventory retrieved",
        data=[SoftwareInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/software/{endpoint_id}", response_model=SuccessResponse[list[SoftwareInventoryResponse]])
async def get_endpoint_software(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: SoftwareInventoryService = Depends(get_software_service)
):
    """Queries details of installed software via target Endpoint UUID identifiers."""
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    records = await service.get_software_inventory(endpoint_id)
    return SuccessResponse(
        message="Software inventory retrieved",
        data=[SoftwareInventoryResponse.model_validate(r) for r in records]
    )


@router.post("/inventory/windows-updates", response_model=SuccessResponse[list[WindowsUpdateInventoryResponse]])
async def upload_windows_updates(
    data: list[WindowsUpdateInventoryCreate],
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: WindowsUpdateInventoryService = Depends(get_windows_update_service)
):
    """Enrolled Windows Agents submit collected Windows Update payloads here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.save_windows_update_inventory(agent_id, data)
    return SuccessResponse(
        message="Windows Update inventory uploaded successfully",
        data=[WindowsUpdateInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/windows-updates", response_model=SuccessResponse[list[WindowsUpdateInventoryResponse]])
async def get_my_windows_updates(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: WindowsUpdateInventoryService = Depends(get_windows_update_service)
):
    """Retrieve the Windows Update inventory linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.get_windows_update_inventory(agent_id)
    return SuccessResponse(
        message="Windows Update inventory retrieved",
        data=[WindowsUpdateInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/windows-updates/{endpoint_id}", response_model=SuccessResponse[list[WindowsUpdateInventoryResponse]])
async def get_endpoint_windows_updates(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: WindowsUpdateInventoryService = Depends(get_windows_update_service)
):
    """Queries details of installed Windows Updates via target Endpoint UUID identifiers."""
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    records = await service.get_windows_update_inventory(endpoint_id)
    return SuccessResponse(
        message="Windows Update inventory retrieved",
        data=[WindowsUpdateInventoryResponse.model_validate(r) for r in records]
    )


@router.post("/inventory/services", response_model=SuccessResponse[list[WindowsServiceInventoryResponse]])
async def upload_windows_services(
    data: list[WindowsServiceInventoryCreate],
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: WindowsServiceInventoryService = Depends(get_windows_service_service)
):
    """Enrolled Windows Agents submit collected Windows Services payload here."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.save_windows_service_inventory(agent_id, data)
    return SuccessResponse(
        message="Windows Service inventory uploaded successfully",
        data=[WindowsServiceInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/services", response_model=SuccessResponse[list[WindowsServiceInventoryResponse]])
async def get_my_windows_services(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    service: WindowsServiceInventoryService = Depends(get_windows_service_service)
):
    """Retrieve the Windows Service inventory linked to the calling agent context."""
    agent_id = await _resolve_authenticated_endpoint(token, db)
    records = await service.get_windows_service_inventory(agent_id)
    return SuccessResponse(
        message="Windows Service inventory retrieved",
        data=[WindowsServiceInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/services/{endpoint_id}", response_model=SuccessResponse[list[WindowsServiceInventoryResponse]])
async def get_endpoint_windows_services(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: WindowsServiceInventoryService = Depends(get_windows_service_service)
):
    """Queries details of installed Windows Services via target Endpoint UUID identifiers."""
    try:
        verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    records = await service.get_windows_service_inventory(endpoint_id)
    return SuccessResponse(
        message="Windows Service inventory retrieved",
        data=[WindowsServiceInventoryResponse.model_validate(r) for r in records]
    )


@router.get("/inventory/{endpoint_id}", response_model=SuccessResponse[HardwareInventoryResponse])
@router.get("/inventory/hardware/{endpoint_id}", response_model=SuccessResponse[HardwareInventoryResponse])
async def get_endpoint_hardware(
    endpoint_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    service: HardwareInventoryService = Depends(get_inventory_service)
):
    """Queries details of custom hardware metrics via target Endpoint UUID identifiers."""
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



