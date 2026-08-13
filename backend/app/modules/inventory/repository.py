import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
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


class HardwareInventoryRepository:
    """Handles persistence operations for HardwareInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint_id(
        self, endpoint_id: uuid.UUID
    ) -> Optional[HardwareInventory]:
        """Queries the hardware inventory record linked to the endpoint UUID."""
        stmt = select(HardwareInventory).where(
            HardwareInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_or_update(
        self, endpoint_id: uuid.UUID, data: HardwareInventoryCreate
    ) -> HardwareInventory:
        """Saves a new hardware configuration record or updates existing matches."""
        record = await self.get_by_endpoint_id(endpoint_id)

        if record:
            # Update fields dynamically
            for key, val in data.model_dump().items():
                setattr(record, key, val)
        else:
            # Insert a new record
            record = HardwareInventory(endpoint_id=endpoint_id, **data.model_dump())
            self.session.add(record)

        await self.session.flush()
        return record


class OperatingSystemInventoryRepository:
    """Handles persistence operations for OperatingSystemInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(
        self, endpoint_id: uuid.UUID
    ) -> Optional[OperatingSystemInventory]:
        """Queries the OS inventory record linked to the endpoint UUID."""
        stmt = select(OperatingSystemInventory).where(
            OperatingSystemInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert(
        self, endpoint_id: uuid.UUID, data: OperatingSystemInventoryCreate
    ) -> OperatingSystemInventory:
        """Upserts an operating system configuration record matching the endpoint UUID."""
        record = await self.get_by_endpoint(endpoint_id)

        if record:
            for key, val in data.model_dump().items():
                setattr(record, key, val)
        else:
            record = OperatingSystemInventory(
                endpoint_id=endpoint_id, **data.model_dump()
            )
            self.session.add(record)

        await self.session.flush()
        return record

    async def update(
        self, endpoint_id: uuid.UUID, data: dict
    ) -> Optional[OperatingSystemInventory]:
        """Directly updates specific fields of the operating system configuration record."""
        record = await self.get_by_endpoint(endpoint_id)
        if record:
            for key, val in data.items():
                if hasattr(record, key):
                    setattr(record, key, val)
            await self.session.flush()
        return record

    async def delete(self, endpoint_id: uuid.UUID) -> bool:
        """Deletes the operating system configuration record linked to the endpoint."""
        record = await self.get_by_endpoint(endpoint_id)
        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False


class NetworkAdapterInventoryRepository:
    """Handles persistence operations for NetworkAdapterInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(
        self, endpoint_id: uuid.UUID
    ) -> list[NetworkAdapterInventory]:
        """Queries all active network adapter records linked to the endpoint UUID."""
        stmt = select(NetworkAdapterInventory).where(
            NetworkAdapterInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_adapters(
        self, endpoint_id: uuid.UUID, data_list: list[NetworkAdapterInventoryCreate]
    ) -> list[NetworkAdapterInventory]:
        """Performs incremental reconciliation (insert/update/delete) on endpoint adapters."""
        existing_adapters = await self.get_by_endpoint(endpoint_id)
        existing_map = {adj.interface_guid: adj for adj in existing_adapters}

        incoming_map = {adj.interface_guid: adj for adj in data_list}
        reconciled = []

        # 1. Update existing or insert new adapters
        for guid, incoming in incoming_map.items():
            if guid in existing_map:
                record = existing_map[guid]
                for key, val in incoming.model_dump().items():
                    setattr(record, key, val)
                reconciled.append(record)
            else:
                record = NetworkAdapterInventory(
                    endpoint_id=endpoint_id, **incoming.model_dump()
                )
                self.session.add(record)
                reconciled.append(record)

        # 2. Delete adapters that are no longer present
        for guid, existing in existing_map.items():
            if guid not in incoming_map:
                await self.session.delete(existing)

        await self.session.flush()
        return reconciled


class StorageInventoryRepository:
    """Handles persistence operations for Physical Disk and Logical Volume database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(
        self, endpoint_id: uuid.UUID
    ) -> list[PhysicalDiskInventory]:
        """Queries all physical disks linked to the endpoint, including nested volumes."""
        stmt = (
            select(PhysicalDiskInventory)
            .where(PhysicalDiskInventory.endpoint_id == endpoint_id)
            .options(selectinload(PhysicalDiskInventory.volumes))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_storage(
        self, endpoint_id: uuid.UUID, data_list: list[PhysicalDiskInventoryCreate]
    ) -> list[PhysicalDiskInventory]:
        """Performs incremental reconciliation of nested disks and volumes."""
        existing_disks = await self.get_by_endpoint(endpoint_id)
        existing_disk_map = {disk.serial_number: disk for disk in existing_disks}

        incoming_disk_map = {disk.serial_number: disk for disk in data_list}
        reconciled_disks = []

        # 1. Reconcile Disks
        for serial, incoming_disk in incoming_disk_map.items():
            if serial in existing_disk_map:
                record = existing_disk_map[serial]
                # Update disk scalar properties
                disk_data = incoming_disk.model_dump(exclude={"volumes"})
                for key, val in disk_data.items():
                    setattr(record, key, val)

                # Reconcile Logical Volumes
                existing_vol_map = {vol.volume_guid: vol for vol in record.volumes}
                incoming_vol_map = {
                    vol.volume_guid: vol for vol in incoming_disk.volumes
                }

                # Update/Insert Volumes
                for v_guid, incoming_vol in incoming_vol_map.items():
                    if v_guid in existing_vol_map:
                        v_record = existing_vol_map[v_guid]
                        for key, val in incoming_vol.model_dump().items():
                            setattr(v_record, key, val)
                    else:
                        v_record = LogicalVolumeInventory(
                            disk_id=record.id, **incoming_vol.model_dump()
                        )
                        self.session.add(v_record)

                # Delete old Volumes
                for v_guid, existing_vol in existing_vol_map.items():
                    if v_guid not in incoming_vol_map:
                        await self.session.delete(existing_vol)

                reconciled_disks.append(record)
            else:
                # Insert brand new Disk with nested Volumes
                disk_data = incoming_disk.model_dump(exclude={"volumes"})
                record = PhysicalDiskInventory(endpoint_id=endpoint_id, **disk_data)
                self.session.add(record)
                await self.session.flush()  # flush to get record.id

                for incoming_vol in incoming_disk.volumes:
                    v_record = LogicalVolumeInventory(
                        disk_id=record.id, **incoming_vol.model_dump()
                    )
                    self.session.add(v_record)

                reconciled_disks.append(record)

        # 2. Delete Disks no longer present
        for serial, existing_disk in existing_disk_map.items():
            if serial not in incoming_disk_map:
                await self.session.delete(existing_disk)

        await self.session.flush()

        # We need to refresh the relationships because we've been modifying them
        stmt = (
            select(PhysicalDiskInventory)
            .where(PhysicalDiskInventory.endpoint_id == endpoint_id)
            .options(selectinload(PhysicalDiskInventory.volumes))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())


class SoftwareInventoryRepository:
    """Handles persistence operations for SoftwareInventory database records with composite key reconciliation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(self, endpoint_id: uuid.UUID) -> list[SoftwareInventory]:
        """Queries all software inventory items associated with the target endpoint UUID."""
        stmt = select(SoftwareInventory).where(
            SoftwareInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_software(
        self, endpoint_id: uuid.UUID, data_list: list[SoftwareInventoryCreate]
    ) -> list[SoftwareInventory]:
        """Performs transactional reconciliation based on (endpoint_id, application_name, publisher, version)."""
        existing_items = await self.get_by_endpoint(endpoint_id)
        existing_map = {
            (item.application_name, item.publisher, item.version): item
            for item in existing_items
        }

        incoming_map = {
            (item.application_name, item.publisher, item.version): item
            for item in data_list
        }
        reconciled = []

        # 1. Update existing or insert new software entries
        for key, incoming in incoming_map.items():
            if key in existing_map:
                record = existing_map[key]
                for attr, val in incoming.model_dump().items():
                    setattr(record, attr, val)
                reconciled.append(record)
            else:
                record = SoftwareInventory(
                    endpoint_id=endpoint_id, **incoming.model_dump()
                )
                self.session.add(record)
                reconciled.append(record)

        # 2. Delete software entries that are no longer installed on the endpoint
        for key, existing in existing_map.items():
            if key not in incoming_map:
                await self.session.delete(existing)

        await self.session.flush()
        return reconciled


class WindowsUpdateInventoryRepository:
    """Handles persistence operations for WindowsUpdateInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(
        self, endpoint_id: uuid.UUID
    ) -> list[WindowsUpdateInventory]:
        """Queries all Windows Update items associated with the target endpoint UUID."""
        stmt = select(WindowsUpdateInventory).where(
            WindowsUpdateInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_updates(
        self, endpoint_id: uuid.UUID, data_list: list[WindowsUpdateInventoryCreate]
    ) -> list[WindowsUpdateInventory]:
        """Performs transactional reconciliation based on (endpoint_id, kb_number)."""
        existing_items = await self.get_by_endpoint(endpoint_id)
        existing_map = {item.kb_number: item for item in existing_items}

        incoming_map = {item.kb_number: item for item in data_list}
        reconciled = []

        # 1. Update existing or insert new update entries
        for key, incoming in incoming_map.items():
            if key in existing_map:
                record = existing_map[key]
                for attr, val in incoming.model_dump().items():
                    setattr(record, attr, val)
                reconciled.append(record)
            else:
                record = WindowsUpdateInventory(
                    endpoint_id=endpoint_id, **incoming.model_dump()
                )
                self.session.add(record)
                reconciled.append(record)

        # 2. Delete update entries that are no longer installed on the endpoint
        for key, existing in existing_map.items():
            if key not in incoming_map:
                await self.session.delete(existing)

        await self.session.flush()
        return reconciled


class WindowsServiceInventoryRepository:
    """Handles persistence operations for WindowsServiceInventory database records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_endpoint(
        self, endpoint_id: uuid.UUID
    ) -> list[WindowsServiceInventory]:
        """Queries all Windows Service items associated with the target endpoint UUID."""
        stmt = select(WindowsServiceInventory).where(
            WindowsServiceInventory.endpoint_id == endpoint_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_services(
        self, endpoint_id: uuid.UUID, data_list: list[WindowsServiceInventoryCreate]
    ) -> list[WindowsServiceInventory]:
        """Performs transactional reconciliation based on (endpoint_id, service_name)."""
        existing_items = await self.get_by_endpoint(endpoint_id)
        existing_map = {item.service_name: item for item in existing_items}

        incoming_map = {item.service_name: item for item in data_list}
        reconciled = []

        # 1. Update existing or insert new service entries
        for key, incoming in incoming_map.items():
            if key in existing_map:
                record = existing_map[key]
                for attr, val in incoming.model_dump().items():
                    setattr(record, attr, val)
                reconciled.append(record)
            else:
                record = WindowsServiceInventory(
                    endpoint_id=endpoint_id, **incoming.model_dump()
                )
                self.session.add(record)
                reconciled.append(record)

        # 2. Delete service entries that are no longer installed on the endpoint
        for key, existing in existing_map.items():
            if key not in incoming_map:
                await self.session.delete(existing)

        await self.session.flush()
        return reconciled
