import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import WindowsUpdateInventory
from app.modules.auth.models import User


@pytest.mark.asyncio
async def test_windows_update_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()

    if not admin:
        admin = User(
            username="admin",
            email="admin_wu_test@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin)
        await db_session.commit()

    # 2. Create dummy endpoint record
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        agent_id=str(uuid.uuid4()),
        hostname="TEST-WU-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hardware-hash-999",
        status="healthy",
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token
    token = create_access_token(
        subject=str(endpoint_id), username="TEST-WU-HOST", roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Initial windows update payload
    payload = [
        {
            "kb_number": "KB5031234",
            "title": "Cumulative Update for Windows 11",
            "description": "Security updates",
            "category": "Security Updates",
            "installed_by": "NT AUTHORITY\\SYSTEM",
            "installed_on": "2026-02-10",
            "support_url": "https://support.microsoft.com",
            "update_id": "uuid-1234",
            "revision_number": 200,
            "operation_result": "Succeeded",
            "severity": "Critical",
            "source": "WMI",
            "is_security_update": True,
            "is_critical_update": True,
            "is_feature_update": False,
            "is_cumulative_update": True,
            "requires_restart": True,
            "is_hidden": False,
            "is_downloaded": True,
            "installed_state": "Installed",
        },
        {
            "kb_number": "KB5045678",
            "title": "Update for Microsoft Defender Antivirus",
            "description": "Definition update",
            "category": "Definition Updates",
            "installed_by": "NT AUTHORITY\\SYSTEM",
            "installed_on": "2026-03-01",
            "support_url": "",
            "update_id": "uuid-5678",
            "revision_number": 201,
            "operation_result": "Succeeded",
            "severity": "Important",
            "source": "COM",
            "is_security_update": True,
            "is_critical_update": False,
            "is_feature_update": False,
            "is_cumulative_update": False,
            "requires_restart": False,
            "is_hidden": False,
            "is_downloaded": True,
            "installed_state": "Installed",
        },
    ]

    # POST to windows-updates endpoint
    post_resp = await client.post(
        "/api/v1/inventory/windows-updates", json=payload, headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 2

    # Direct DB verification
    stmt_wu = select(WindowsUpdateInventory).where(
        WindowsUpdateInventory.endpoint_id == endpoint_id
    )
    db_res = await db_session.execute(stmt_wu)
    db_records = db_res.scalars().all()
    assert len(db_records) == 2

    # 5. Test Reconciliation (update KB5031234 title, delete KB5045678, add KB5099999)
    payload_reconcile = [
        {
            "kb_number": "KB5031234",
            "title": "Cumulative Update for Windows 11 (Modified)",
            "description": "Security updates",
            "category": "Security Updates",
            "installed_by": "NT AUTHORITY\\SYSTEM",
            "installed_on": "2026-02-10",
            "support_url": "https://support.microsoft.com",
            "update_id": "uuid-1234",
            "revision_number": 200,
            "operation_result": "Succeeded",
            "severity": "Critical",
            "source": "WMI",
            "is_security_update": True,
            "is_critical_update": True,
            "is_feature_update": False,
            "is_cumulative_update": True,
            "requires_restart": True,
            "is_hidden": False,
            "is_downloaded": True,
            "installed_state": "Installed",
        },
        {
            "kb_number": "KB5099999",
            "title": "Feature Update to Windows 11, version 24H2",
            "description": "Feature update",
            "category": "Upgrades",
            "installed_by": "NT AUTHORITY\\SYSTEM",
            "installed_on": "2026-04-15",
            "support_url": "https://support.microsoft.com",
            "update_id": "uuid-9999",
            "revision_number": 100,
            "operation_result": "Succeeded",
            "severity": "Important",
            "source": "COM",
            "is_security_update": False,
            "is_critical_update": False,
            "is_feature_update": True,
            "is_cumulative_update": False,
            "requires_restart": True,
            "is_hidden": False,
            "is_downloaded": True,
            "installed_state": "Installed",
        },
    ]

    post_rec = await client.post(
        "/api/v1/inventory/windows-updates",
        json=payload_reconcile,
        headers=auth_headers,
    )
    assert post_rec.status_code == 200

    # Verify reconciliation in DB
    db_res_rec = await db_session.execute(stmt_wu)
    db_records_rec = db_res_rec.scalars().all()
    assert len(db_records_rec) == 2
    kbs = [r.kb_number for r in db_records_rec]
    assert "KB5031234" in kbs
    assert "KB5099999" in kbs
    assert "KB5045678" not in kbs

    kb1_record = next(r for r in db_records_rec if r.kb_number == "KB5031234")
    assert kb1_record.title == "Cumulative Update for Windows 11 (Modified)"

    # 6. GET self windows update inventory
    get_resp = await client.get(
        "/api/v1/inventory/windows-updates", headers=auth_headers
    )
    assert get_resp.status_code == 200
    assert len(get_resp.json()["data"]) == 2

    # 7. GET windows update inventory by endpoint_id
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/windows-updates/{endpoint_id}", headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert len(get_by_id_resp.json()["data"]) == 2

    # 8. Unauthenticated access fails
    unauth_resp = await client.get("/api/v1/inventory/windows-updates")
    assert unauth_resp.status_code == 401
