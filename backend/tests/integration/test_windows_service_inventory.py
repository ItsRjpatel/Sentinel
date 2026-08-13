import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import WindowsServiceInventory
from app.modules.auth.models import User


@pytest.mark.asyncio
async def test_windows_service_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()

    if not admin:
        admin = User(
            username="admin",
            email="admin_ws_test@example.com",
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
        hostname="TEST-WS-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hardware-hash-777",
        status="healthy",
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token
    token = create_access_token(
        subject=str(endpoint_id), username="TEST-WS-HOST", roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Initial windows service payload
    payload = [
        {
            "service_name": "WinDefend",
            "display_name": "Microsoft Defender Antivirus Service",
            "description": "Helps protect users from malware and other potentially unwanted software",
            "executable_path": "C:\\ProgramData\\Microsoft\\Windows Defender\\platform\\4.18.23070.1004-0\\MsMpEng.exe",
            "current_state": "Running",
            "start_mode": "Auto",
            "start_type": "Automatic",
            "service_type": "Win32OwnProcess",
            "account_name": "LocalSystem",
            "process_id": 1234,
            "binary_path": "C:\\ProgramData\\Microsoft\\Windows Defender\\platform\\4.18.23070.1004-0\\MsMpEng.exe",
            "delayed_auto_start": False,
            "error_control": "Normal",
            "dependencies": "RpcSs",
            "dependent_services": "WdNisSvc",
            "can_stop": True,
            "can_pause": False,
            "can_shutdown": False,
            "desktop_interaction": False,
            "tag_id": 0,
            "is_critical": True,
            "digital_signature_status": "Valid",
        },
        {
            "service_name": "Spooler",
            "display_name": "Print Spooler",
            "description": "This service spools print jobs and handles interaction with the printer.",
            "executable_path": "C:\\Windows\\System32\\spoolsv.exe",
            "current_state": "Running",
            "start_mode": "Auto",
            "start_type": "Automatic",
            "service_type": "Win32OwnProcess",
            "account_name": "LocalSystem",
            "process_id": 5678,
            "binary_path": "C:\\Windows\\System32\\spoolsv.exe",
            "delayed_auto_start": False,
            "error_control": "Normal",
            "dependencies": "RPCSS, http",
            "dependent_services": "Fax",
            "can_stop": True,
            "can_pause": False,
            "can_shutdown": False,
            "desktop_interaction": False,
            "tag_id": 0,
            "is_critical": False,
            "digital_signature_status": "Valid",
        },
    ]

    # POST to services endpoint
    post_resp = await client.post(
        "/api/v1/inventory/services", json=payload, headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 2

    # Direct DB verification
    stmt_ws = select(WindowsServiceInventory).where(
        WindowsServiceInventory.endpoint_id == endpoint_id
    )
    db_res = await db_session.execute(stmt_ws)
    db_records = db_res.scalars().all()
    assert len(db_records) == 2

    # 5. Test Reconciliation (update WinDefend state to Stopped, delete Spooler, add BITS)
    payload_reconcile = [
        {
            "service_name": "WinDefend",
            "display_name": "Microsoft Defender Antivirus Service",
            "description": "Helps protect users from malware and other potentially unwanted software",
            "executable_path": "C:\\ProgramData\\Microsoft\\Windows Defender\\platform\\4.18.23070.1004-0\\MsMpEng.exe",
            "current_state": "Stopped",
            "start_mode": "Disabled",
            "start_type": "Disabled",
            "service_type": "Win32OwnProcess",
            "account_name": "LocalSystem",
            "process_id": 0,
            "binary_path": "C:\\ProgramData\\Microsoft\\Windows Defender\\platform\\4.18.23070.1004-0\\MsMpEng.exe",
            "delayed_auto_start": False,
            "error_control": "Normal",
            "dependencies": "RpcSs",
            "dependent_services": "WdNisSvc",
            "can_stop": False,
            "can_pause": False,
            "can_shutdown": False,
            "desktop_interaction": False,
            "tag_id": 0,
            "is_critical": True,
            "digital_signature_status": "Valid",
        },
        {
            "service_name": "BITS",
            "display_name": "Background Intelligent Transfer Service",
            "description": "Transfers files in the background using idle network bandwidth.",
            "executable_path": "C:\\Windows\\System32\\svchost.exe -k netsvcs",
            "current_state": "Running",
            "start_mode": "Manual",
            "start_type": "Manual",
            "service_type": "Win32ShareProcess",
            "account_name": "LocalSystem",
            "process_id": 9999,
            "binary_path": "C:\\Windows\\System32\\svchost.exe -k netsvcs",
            "delayed_auto_start": True,
            "error_control": "Normal",
            "dependencies": "RpcSs, EventSystem",
            "dependent_services": "",
            "can_stop": True,
            "can_pause": False,
            "can_shutdown": False,
            "desktop_interaction": False,
            "tag_id": 0,
            "is_critical": False,
            "digital_signature_status": "Valid",
        },
    ]

    post_rec = await client.post(
        "/api/v1/inventory/services", json=payload_reconcile, headers=auth_headers
    )
    assert post_rec.status_code == 200

    # Verify reconciliation in DB
    db_res_rec = await db_session.execute(stmt_ws)
    db_records_rec = db_res_rec.scalars().all()
    assert len(db_records_rec) == 2
    services = [r.service_name for r in db_records_rec]
    assert "WinDefend" in services
    assert "BITS" in services
    assert "Spooler" not in services

    windefend_record = next(r for r in db_records_rec if r.service_name == "WinDefend")
    assert windefend_record.current_state == "Stopped"

    # 6. GET self windows service inventory
    get_resp = await client.get("/api/v1/inventory/services", headers=auth_headers)
    assert get_resp.status_code == 200
    assert len(get_resp.json()["data"]) == 2

    # 7. GET windows service inventory by endpoint_id
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/services/{endpoint_id}", headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert len(get_by_id_resp.json()["data"]) == 2

    # 8. Unauthenticated access fails
    unauth_resp = await client.get("/api/v1/inventory/services")
    assert unauth_resp.status_code == 401
