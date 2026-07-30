import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import OperatingSystemInventory
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_os_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create a dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin_os_test@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True
        )
        db_session.add(admin)
        await db_session.commit()
    
    # 2. Create a dummy endpoint record
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        hostname="TEST-OS-HOST",
        os_version="Windows 11 (Build 22621)",
        hardware_hash="fake-hardware-hash-999",
        status="healthy"
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token representing this endpoint
    token = create_access_token(
        subject=str(endpoint_id),
        username="TEST-OS-HOST",
        roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. OS inventory payload
    payload = {
        "computer_name": "TEST-OS-HOST",
        "os_name": "Microsoft Windows 11 Enterprise",
        "edition": "Enterprise",
        "version": "10.0.22621",
        "build_number": "22621",
        "display_version": "22H2",
        "install_date": "20231015092040.000000+120",
        "last_boot_time": "20260728100532.000000+330",
        "uptime_seconds": 172800,  # 2 days
        "system_architecture": "64-bit",
        "product_type": "1",
        "registered_owner": "Test User",
        "registered_organization": "Test Org",
        "windows_directory": "C:\\Windows",
        "system_directory": "C:\\Windows\\System32",
        "boot_device": "\\Device\\HarddiskVolume1",
        "system_drive": "C:",
        "locale": "0409",
        "time_zone": "UTC+5:30",
        "domain_workgroup": "WORKGROUP",
        "activation_status": "Licensed"
    }

    # POST to OS inventory route
    post_resp = await client.post(
        "/api/v1/inventory/os",
        json=payload,
        headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert res_data["data"]["computer_name"] == "TEST-OS-HOST"
    assert res_data["data"]["uptime_seconds"] == 172800

    # Verify database directly
    stmt = select(OperatingSystemInventory).where(OperatingSystemInventory.endpoint_id == endpoint_id)
    db_res = await db_session.execute(stmt)
    db_record = db_res.scalar_one_or_none()
    assert db_record is not None
    assert db_record.computer_name == "TEST-OS-HOST"
    assert db_record.uptime_seconds == 172800

    # 5. GET self OS inventory
    get_resp = await client.get(
        "/api/v1/inventory/os",
        headers=auth_headers
    )
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["success"] is True
    assert get_data["data"]["os_name"] == "Microsoft Windows 11 Enterprise"

    # 6. GET other endpoint OS inventory by ID
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/os/{endpoint_id}",
        headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert get_by_id_resp.json()["data"]["build_number"] == "22621"

    # 7. Duplicate upload updates the same record (no extra rows created)
    payload_update = dict(payload)
    payload_update["uptime_seconds"] = 180000
    post_dup = await client.post(
        "/api/v1/inventory/os",
        json=payload_update,
        headers=auth_headers
    )
    assert post_dup.status_code == 200
    
    # Assert database still has exactly one record for this endpoint, and values updated
    stmt_check = select(OperatingSystemInventory).where(OperatingSystemInventory.endpoint_id == endpoint_id)
    db_res_check = await db_session.execute(stmt_check)
    db_records = db_res_check.scalars().all()
    assert len(db_records) == 1
    assert db_records[0].uptime_seconds == 180000

    # 8. Invalid payload fields returns 422
    payload_invalid = dict(payload)
    payload_invalid["uptime_seconds"] = -100  # Invalid under 'ge=0' constraint
    post_invalid = await client.post(
        "/api/v1/inventory/os",
        json=payload_invalid,
        headers=auth_headers
    )
    assert post_invalid.status_code == 422

    # 9. Access without auth header returns 401
    unauth_resp = await client.get("/api/v1/inventory/os")
    assert unauth_resp.status_code == 401
