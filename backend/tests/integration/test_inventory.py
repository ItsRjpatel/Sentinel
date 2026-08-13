import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import HardwareInventory
from app.modules.auth.models import User


@pytest.mark.asyncio
async def test_hardware_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create a dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()

    if not admin:
        admin = User(
            username="admin",
            email="admin_inventory_test@example.com",
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
        hostname="TEST-HOST",
        os_version="Windows 11 (Build 22621)",
        hardware_hash="fake-hardware-hash-999",
        status="healthy",
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token representing this endpoint
    token = create_access_token(
        subject=str(endpoint_id), username="TEST-HOST", roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Upload hardware inventory
    payload = {
        "manufacturer": "Dell Inc.",
        "model": "OptiPlex 7080",
        "serial_number": "MXL123456",
        "bios_version": "1.8.1",
        "bios_manufacturer": "Dell",
        "bios_release_date": "2023-01-01",
        "motherboard": "0DFX2D",
        "cpu_name": "Intel Core i7-10700",
        "cpu_architecture": "x64",
        "cpu_cores": 8,
        "cpu_logical_processors": 16,
        "installed_ram_bytes": 17179869184,  # 16 GB in bytes
        "tpm_version": "2.0",
        "secure_boot_enabled": True,
        "is_virtual": False,
    }

    # POST to inventory upload route
    post_resp = await client.post(
        "/api/v1/inventory/hardware", json=payload, headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert res_data["data"]["manufacturer"] == "Dell Inc."
    assert res_data["data"]["cpu_cores"] == 8
    assert res_data["data"]["installed_ram_bytes"] == 17179869184

    # Verify database directly (Audit Check)
    stmt = select(HardwareInventory).where(HardwareInventory.endpoint_id == endpoint_id)
    db_res = await db_session.execute(stmt)
    db_record = db_res.scalar_one_or_none()
    assert db_record is not None
    assert db_record.manufacturer == "Dell Inc."
    assert db_record.installed_ram_bytes == 17179869184

    # 5. GET self hardware inventory
    get_resp = await client.get("/api/v1/inventory/hardware", headers=auth_headers)
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["success"] is True
    assert get_data["data"]["serial_number"] == "MXL123456"

    # 6. GET other endpoint hardware inventory by ID
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/{endpoint_id}", headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert get_by_id_resp.json()["data"]["model"] == "OptiPlex 7080"

    # 7. Access without auth header returns 401
    unauth_resp = await client.get("/api/v1/inventory/hardware")
    assert unauth_resp.status_code == 401
