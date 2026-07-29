import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.inventory.repository import HardwareInventoryRepository
from app.modules.inventory.models import HardwareInventory
from app.modules.inventory.schemas import HardwareInventoryCreate

class HardwareInventoryService:
    """Manages transactional logic for hardware inventory aggregation and uploads."""

    def __init__(self, session: AsyncSession, repo: HardwareInventoryRepository) -> None:
        self.session = session
        self.repo = repo

    async def get_hardware_inventory(self, endpoint_id: uuid.UUID) -> Optional[HardwareInventory]:
        """Retrieves hardware specifications mapped to the endpoint ID."""
        return await self.repo.get_by_endpoint_id(endpoint_id)

    async def save_hardware_inventory(
        self,
        endpoint_id: uuid.UUID,
        data: HardwareInventoryCreate
    ) -> HardwareInventory:
        """Saves and commits changes to hardware inventory data."""
        record = await self.repo.create_or_update(endpoint_id, data)
        await self.session.commit()
        return record
