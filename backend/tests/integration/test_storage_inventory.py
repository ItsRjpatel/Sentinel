import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import PhysicalDiskInventory, LogicalVolumeInventory
from app.modules.auth.models import User


@pytest.mark.asyncio
async def test_storage_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create a dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()

    if not admin:
        admin = User(
            username="admin",
            email="admin_storage_test@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin)
        await db_session.commit()

    # 2. Create a dummy endpoint record
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        agent_id=str(uuid.uuid4()),
        hostname="TEST-STORAGE-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hardware-hash-777",
        status="healthy",
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token representing this endpoint
    token = create_access_token(
        subject=str(endpoint_id), username="TEST-STORAGE-HOST", roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Initial storage payload
    vol_guid_1 = str(uuid.uuid4())
    vol_guid_2 = str(uuid.uuid4())

    payload = [
        {
            "disk_number": 0,
            "model": "Samsung SSD 970 EVO",
            "manufacturer": "Samsung",
            "serial_number": "S462NX0K",
            "firmware_version": "2B2QEXM7",
            "media_type": "SSD",
            "bus_type": "NVMe",
            "interface_type": "SCSI",
            "size_bytes": 500107862016,
            "partition_count": 3,
            "health_status": "Healthy",
            "operational_status": "Online",
            "is_boot_disk": True,
            "is_system_disk": True,
            "is_removable": False,
            "is_virtual": False,
            "volumes": [
                {
                    "drive_letter": "C:",
                    "volume_name": "Windows",
                    "volume_guid": vol_guid_1,
                    "file_system": "NTFS",
                    "label": "Windows",
                    "capacity_bytes": 499000000000,
                    "free_space_bytes": 100000000000,
                    "used_space_bytes": 399000000000,
                    "compression_enabled": False,
                    "bitlocker_status": "Fully Encrypted",
                    "volume_type": "Local Disk",
                    "is_boot_volume": True,
                    "is_system_volume": True,
                    "shadow_copy_support": True,
                },
                {
                    "drive_letter": "D:",
                    "volume_name": "Data",
                    "volume_guid": vol_guid_2,
                    "file_system": "NTFS",
                    "label": "Data",
                    "capacity_bytes": 1000000000000,
                    "free_space_bytes": 500000000000,
                    "used_space_bytes": 500000000000,
                    "compression_enabled": False,
                    "bitlocker_status": "Unencrypted",
                    "volume_type": "Local Disk",
                    "is_boot_volume": False,
                    "is_system_volume": False,
                    "shadow_copy_support": False,
                },
            ],
        }
    ]

    # POST to storage route
    post_resp = await client.post(
        "/api/v1/inventory/storage", json=payload, headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 1
    assert len(res_data["data"][0]["volumes"]) == 2

    # Verify database directly
    stmt = select(PhysicalDiskInventory).where(
        PhysicalDiskInventory.endpoint_id == endpoint_id
    )
    db_res = await db_session.execute(stmt)
    db_records = db_res.scalars().all()
    assert len(db_records) == 1
    disk_id = db_records[0].id

    stmt_vol = select(LogicalVolumeInventory).where(
        LogicalVolumeInventory.disk_id == disk_id
    )
    db_res_vol = await db_session.execute(stmt_vol)
    db_vols = db_res_vol.scalars().all()
    assert len(db_vols) == 2

    # 5. Incremental Reconciliation test
    # We update disk size, update volume C, remove volume D, add volume E, and add a second USB Disk
    vol_guid_3 = str(uuid.uuid4())
    payload_reconcile = [
        {
            "disk_number": 0,
            "model": "Samsung SSD 970 EVO",
            "manufacturer": "Samsung",
            "serial_number": "S462NX0K",
            "firmware_version": "2B2QEXM7",
            "media_type": "SSD",
            "bus_type": "NVMe",
            "interface_type": "SCSI",
            "size_bytes": 600000000000,  # Updated size
            "partition_count": 3,
            "health_status": "Healthy",
            "operational_status": "Online",
            "is_boot_disk": True,
            "is_system_disk": True,
            "is_removable": False,
            "is_virtual": False,
            "volumes": [
                {
                    # Updated volume C
                    "drive_letter": "C:",
                    "volume_name": "Windows_Updated",
                    "volume_guid": vol_guid_1,
                    "file_system": "NTFS",
                    "label": "Windows",
                    "capacity_bytes": 499000000000,
                    "free_space_bytes": 50000000000,  # Updated free space
                    "used_space_bytes": 449000000000,
                    "compression_enabled": False,
                    "bitlocker_status": "Fully Encrypted",
                    "volume_type": "Local Disk",
                    "is_boot_volume": True,
                    "is_system_volume": True,
                    "shadow_copy_support": True,
                },
                {
                    # New volume E
                    "drive_letter": "E:",
                    "volume_name": "NewData",
                    "volume_guid": vol_guid_3,
                    "file_system": "ReFS",
                    "label": "NewData",
                    "capacity_bytes": 1000000000000,
                    "free_space_bytes": 1000000000000,
                    "used_space_bytes": 0,
                    "compression_enabled": False,
                    "bitlocker_status": "Unencrypted",
                    "volume_type": "Local Disk",
                    "is_boot_volume": False,
                    "is_system_volume": False,
                    "shadow_copy_support": False,
                },
            ],
        },
        {
            # New Disk (USB)
            "disk_number": 1,
            "model": "SanDisk Cruzer",
            "manufacturer": "SanDisk",
            "serial_number": "SD123456789",
            "firmware_version": "1.0",
            "media_type": "HDD",
            "bus_type": "USB",
            "interface_type": "USB",
            "size_bytes": 32000000000,
            "partition_count": 1,
            "health_status": "Healthy",
            "operational_status": "Online",
            "is_boot_disk": False,
            "is_system_disk": False,
            "is_removable": True,
            "is_virtual": False,
            "volumes": [],
        },
    ]

    post_rec = await client.post(
        "/api/v1/inventory/storage", json=payload_reconcile, headers=auth_headers
    )
    assert post_rec.status_code == 200

    # Verify reconciliation in DB
    stmt_rec = select(PhysicalDiskInventory).where(
        PhysicalDiskInventory.endpoint_id == endpoint_id
    )
    db_res_rec = await db_session.execute(stmt_rec)
    db_records_rec = db_res_rec.scalars().all()
    assert len(db_records_rec) == 2

    # 6. GET self storage inventory
    get_resp = await client.get("/api/v1/inventory/storage", headers=auth_headers)
    assert get_resp.status_code == 200
    assert len(get_resp.json()["data"]) == 2

    # 7. GET other endpoint storage inventory by ID
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/storage/{endpoint_id}", headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert len(get_by_id_resp.json()["data"]) == 2

    # 8. Access without auth header returns 401
    unauth_resp = await client.get("/api/v1/inventory/storage")
    assert unauth_resp.status_code == 401
