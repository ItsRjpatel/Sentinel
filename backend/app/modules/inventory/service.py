import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.inventory.repository import (
    HardwareInventoryRepository,
    OperatingSystemInventoryRepository,
    NetworkAdapterInventoryRepository,
    StorageInventoryRepository,
    SoftwareInventoryRepository,
    WindowsUpdateInventoryRepository,
    WindowsServiceInventoryRepository,
)
from app.modules.inventory.models import (
    HardwareInventory,
    OperatingSystemInventory,
    NetworkAdapterInventory,
    PhysicalDiskInventory,
    LogicalVolumeInventory,
    SoftwareInventory,
    WindowsUpdateInventory,
    WindowsServiceInventory,
)
from app.modules.inventory.schemas import (
    HardwareInventoryCreate,
    OperatingSystemInventoryCreate,
    NetworkAdapterInventoryCreate,
    PhysicalDiskInventoryCreate,
    SoftwareInventoryCreate,
    WindowsUpdateInventoryCreate,
    WindowsServiceInventoryCreate,
)


class HardwareInventoryService:
    """Manages transactional logic for hardware inventory aggregation and uploads."""

    def __init__(
        self, session: AsyncSession, repo: HardwareInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_hardware_inventory(
        self, endpoint_id: uuid.UUID
    ) -> Optional[HardwareInventory]:
        """Retrieves hardware specifications mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint_id(endpoint_id)

    async def save_hardware_inventory(
        self, endpoint_id: uuid.UUID, data: HardwareInventoryCreate
    ) -> HardwareInventory:
        """Saves and commits changes to hardware inventory data."""
        record = await self.repo.create_or_update(endpoint_id, data)
        await self.session.commit()
        return record


class OperatingSystemInventoryService:
    """Manages transactional business logic for Operating System inventory collection."""

    def __init__(
        self, session: AsyncSession, repo: OperatingSystemInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_os_inventory(
        self, endpoint_id: uuid.UUID
    ) -> Optional[OperatingSystemInventory]:
        """Retrieves operating system details linked to the endpoint UUID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_os_inventory(
        self, endpoint_id: uuid.UUID, data: OperatingSystemInventoryCreate
    ) -> OperatingSystemInventory:
        """Upserts OS details and commits the active database transaction."""
        record = await self.repo.upsert(endpoint_id, data)
        await self.session.commit()
        return record

    async def delete_os_inventory(self, endpoint_id: uuid.UUID) -> bool:
        """Deletes OS details and commits the database transaction."""
        success = await self.repo.delete(endpoint_id)
        if success:
            await self.session.commit()
        return success


class NetworkAdapterInventoryService:
    """Manages transactional business logic for network adapter inventory collection."""

    def __init__(
        self, session: AsyncSession, repo: NetworkAdapterInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_network_inventory(
        self, endpoint_id: uuid.UUID
    ) -> list[NetworkAdapterInventory]:
        """Retrieves all network adapter records mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_network_inventory(
        self, endpoint_id: uuid.UUID, data_list: list[NetworkAdapterInventoryCreate]
    ) -> list[NetworkAdapterInventory]:
        """Saves and commits changes to network adapter inventory data."""
        records = await self.repo.upsert_adapters(endpoint_id, data_list)
        await self.session.commit()
        return records


class StorageInventoryService:
    """Manages transactional business logic for storage inventory collection."""

    def __init__(self, session: AsyncSession, repo: StorageInventoryRepository) -> None:
        self.session = session
        self.repo = repo

    async def get_storage_inventory(
        self, endpoint_id: uuid.UUID
    ) -> list[PhysicalDiskInventory]:
        """Retrieves all physical disk and volume records mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_storage_inventory(
        self, endpoint_id: uuid.UUID, data_list: list[PhysicalDiskInventoryCreate]
    ) -> list[PhysicalDiskInventory]:
        """Saves and commits changes to nested storage inventory data."""
        records = await self.repo.upsert_storage(endpoint_id, data_list)
        await self.session.commit()
        return records


class SoftwareInventoryService:
    """Manages transactional business logic for installed software inventory collection."""

    def __init__(
        self, session: AsyncSession, repo: SoftwareInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_software_inventory(
        self, endpoint_id: uuid.UUID
    ) -> list[SoftwareInventory]:
        """Retrieves all installed software records mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_software_inventory(
        self, endpoint_id: uuid.UUID, data_list: list[SoftwareInventoryCreate]
    ) -> list[SoftwareInventory]:
        """Saves and commits changes to installed software inventory data."""
        records = await self.repo.upsert_software(endpoint_id, data_list)
        await self.session.commit()
        return records


class WindowsUpdateInventoryService:
    """Manages transactional business logic for Windows Update inventory collection."""

    def __init__(
        self, session: AsyncSession, repo: WindowsUpdateInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_windows_update_inventory(
        self, endpoint_id: uuid.UUID
    ) -> list[WindowsUpdateInventory]:
        """Retrieves all Windows Update records mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_windows_update_inventory(
        self, endpoint_id: uuid.UUID, data_list: list[WindowsUpdateInventoryCreate]
    ) -> list[WindowsUpdateInventory]:
        """Saves and commits changes to Windows Update inventory data."""
        records = await self.repo.upsert_updates(endpoint_id, data_list)
        await self.session.commit()
        return records


class WindowsServiceInventoryService:
    """Manages transactional business logic for Windows Service inventory collection."""

    def __init__(
        self, session: AsyncSession, repo: WindowsServiceInventoryRepository
    ) -> None:
        self.session = session
        self.repo = repo

    async def get_windows_service_inventory(
        self, endpoint_id: uuid.UUID
    ) -> list[WindowsServiceInventory]:
        """Retrieves all Windows Service records mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint(endpoint_id)

    async def save_windows_service_inventory(
        self, endpoint_id: uuid.UUID, data_list: list[WindowsServiceInventoryCreate]
    ) -> list[WindowsServiceInventory]:
        """Saves and commits changes to Windows Service inventory data."""
        records = await self.repo.upsert_services(endpoint_id, data_list)
        await self.session.commit()
        return records
