import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import SoftwareInventory
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_software_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin_sw_test@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True
        )
        db_session.add(admin)
        await db_session.commit()

    # 2. Create dummy endpoint record
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        hostname="TEST-SW-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hardware-hash-888",
        status="healthy"
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token
    token = create_access_token(
        subject=str(endpoint_id),
        username="TEST-SW-HOST",
        roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Initial software payload
    payload = [
        {
            "application_name": "Google Chrome",
            "publisher": "Google LLC",
            "version": "120.0.6099.109",
            "install_date": "2026-01-15",
            "install_location": "C:\\Program Files\\Google\\Chrome\\Application",
            "estimated_size_kb": 450000,
            "uninstall_string": "MsiExec.exe /X{CHROME-GUID}",
            "install_source": "C:\\Installers\\Chrome",
            "architecture": "x64",
            "language": "1033",
            "product_code": "{CHROME-GUID}",
            "system_component": False,
            "windows_installer": True,
            "url_info": "https://www.google.com/chrome",
            "help_link": "https://support.google.com/chrome",
            "modify_path": "",
            "install_scope": "Per-machine",
            "registry_key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{CHROME-GUID}"
        },
        {
            "application_name": "7-Zip 23.01 (x64)",
            "publisher": "Igor Pavlov",
            "version": "23.01",
            "install_date": "2025-11-20",
            "install_location": "C:\\Program Files\\7-Zip",
            "estimated_size_kb": 5000,
            "uninstall_string": "\"C:\\Program Files\\7-Zip\\Uninstall.exe\"",
            "install_source": "",
            "architecture": "x64",
            "language": "1033",
            "product_code": "7-Zip",
            "system_component": False,
            "windows_installer": False,
            "url_info": "https://www.7-zip.org",
            "help_link": "",
            "modify_path": "",
            "install_scope": "Per-machine",
            "registry_key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\7-Zip"
        }
    ]

    # POST to software endpoint
    post_resp = await client.post(
        "/api/v1/inventory/software",
        json=payload,
        headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 2

    # Direct DB verification
    stmt_sw = select(SoftwareInventory).where(SoftwareInventory.endpoint_id == endpoint_id)
    db_res = await db_session.execute(stmt_sw)
    db_records = db_res.scalars().all()
    assert len(db_records) == 2

    # 5. Test Reconciliation (update Chrome version, delete 7-Zip, add Notepad++)
    payload_reconcile = [
        {
            "application_name": "Google Chrome",
            "publisher": "Google LLC",
            "version": "121.0.6167.85", # Version update
            "install_date": "2026-01-15",
            "install_location": "C:\\Program Files\\Google\\Chrome\\Application",
            "estimated_size_kb": 460000,
            "uninstall_string": "MsiExec.exe /X{CHROME-GUID}",
            "install_source": "C:\\Installers\\Chrome",
            "architecture": "x64",
            "language": "1033",
            "product_code": "{CHROME-GUID}",
            "system_component": False,
            "windows_installer": True,
            "url_info": "https://www.google.com/chrome",
            "help_link": "https://support.google.com/chrome",
            "modify_path": "",
            "install_scope": "Per-machine",
            "registry_key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{CHROME-GUID}"
        },
        {
            "application_name": "Notepad++ (64-bit x64)",
            "publisher": "Notepad++ Team",
            "version": "8.6.2",
            "install_date": "2026-02-01",
            "install_location": "C:\\Program Files\\Notepad++",
            "estimated_size_kb": 12000,
            "uninstall_string": "\"C:\\Program Files\\Notepad++\\uninstall.exe\"",
            "install_source": "",
            "architecture": "x64",
            "language": "1033",
            "product_code": "Notepad++",
            "system_component": False,
            "windows_installer": False,
            "url_info": "https://notepad-plus-plus.org",
            "help_link": "",
            "modify_path": "",
            "install_scope": "Per-machine",
            "registry_key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Notepad++"
        }
    ]

    post_rec = await client.post(
        "/api/v1/inventory/software",
        json=payload_reconcile,
        headers=auth_headers
    )
    assert post_rec.status_code == 200

    # Verify reconciliation in DB
    db_res_rec = await db_session.execute(stmt_sw)
    db_records_rec = db_res_rec.scalars().all()
    assert len(db_records_rec) == 2
    app_names = [r.application_name for r in db_records_rec]
    assert "Google Chrome" in app_names
    assert "Notepad++ (64-bit x64)" in app_names
    assert "7-Zip 23.01 (x64)" not in app_names

    # 6. GET self software inventory
    get_resp = await client.get(
        "/api/v1/inventory/software",
        headers=auth_headers
    )
    assert get_resp.status_code == 200
    assert len(get_resp.json()["data"]) == 2

    # 7. GET software inventory by endpoint_id
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/software/{endpoint_id}",
        headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert len(get_by_id_resp.json()["data"]) == 2

    # 8. Unauthenticated access fails
    unauth_resp = await client.get("/api/v1/inventory/software")
    assert unauth_resp.status_code == 401
