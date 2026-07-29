import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.inventory.models import HardwareInventory
from app.modules.inventory.schemas import HardwareInventoryCreate

class HardwareInventoryRepository:
    """Handles persistence operations for HardwareInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint_id(self, endpoint_id: uuid.UUID) -> Optional[HardwareInventory]:
        """Queries the hardware inventory record linked to the endpoint UUID."""
        stmt = select(HardwareInventory).where(HardwareInventory.endpoint_id == endpoint_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_or_update(
        self,
        endpoint_id: uuid.UUID,
        data: HardwareInventoryCreate
    ) -> HardwareInventory:
        """Saves a new hardware configuration record or updates existing matches."""
        record = await self.get_by_endpoint_id(endpoint_id)

        if record:
            # Update fields dynamically
            for key, val in data.model_dump().items():
                setattr(record, key, val)
        else:
            # Insert a new record
            record = HardwareInventory(
                endpoint_id=endpoint_id,
                **data.model_dump()
            )
            self.session.add(record)

        await self.session.flush()
        return record
