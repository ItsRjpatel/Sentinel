import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.core.security import create_access_token
from app.modules.endpoints.models import Endpoint
from app.modules.inventory.models import NetworkAdapterInventory
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_network_inventory_flow(client: AsyncClient, db_session):
    # 1. Fetch or create a dummy admin user
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin_net_test@example.com",
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
        hostname="TEST-NET-HOST",
        os_version="Windows 11 (Build 22621)",
        hardware_hash="fake-hardware-hash-999",
        status="healthy"
    )
    db_session.add(endpoint)
    await db_session.commit()

    # 3. Generate access token representing this endpoint
    token = create_access_token(
        subject=str(endpoint_id),
        username="TEST-NET-HOST",
        roles=[]
    )
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 4. Initial network adapters payload
    adapter_guid_1 = str(uuid.uuid4())
    adapter_guid_2 = str(uuid.uuid4())
    
    payload = [
        {
            "hostname": "TEST-NET-HOST",
            "domain_workgroup": "WORKGROUP",
            "adapter_name": "Ethernet Adapter 1",
            "adapter_description": "Intel(R) Ethernet Connection I219-LM",
            "interface_guid": adapter_guid_1,
            "mac_address": "00:11:22:33:44:55",
            "ipv4": "192.168.1.100",
            "ipv6": "fe80::11",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns_servers": "8.8.8.8,8.8.4.4",
            "dhcp_enabled": True,
            "dhcp_server": "192.168.1.1",
            "lease_obtained": "2026-07-29T10:00:00Z",
            "lease_expires": "2026-07-30T10:00:00Z",
            "interface_speed": 1000000000,
            "interface_type": "Ethernet",
            "operational_status": "Connected",
            "is_physical": True,
            "connection_type": "Ethernet",
            "is_vpn": False
        },
        {
            "hostname": "TEST-NET-HOST",
            "domain_workgroup": "WORKGROUP",
            "adapter_name": "Wi-Fi Adapter 2",
            "adapter_description": "Intel(R) Wi-Fi 6 AX201",
            "interface_guid": adapter_guid_2,
            "mac_address": "00:11:22:33:44:66",
            "ipv4": "192.168.1.101",
            "ipv6": "fe80::22",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns_servers": "8.8.8.8",
            "dhcp_enabled": True,
            "dhcp_server": "192.168.1.1",
            "lease_obtained": "2026-07-29T10:05:00Z",
            "lease_expires": "2026-07-30T10:05:00Z",
            "interface_speed": 866000000,
            "interface_type": "Wireless",
            "operational_status": "Connected",
            "is_physical": True,
            "connection_type": "WiFi",
            "is_vpn": False
        }
    ]

    # POST to network route
    post_resp = await client.post(
        "/api/v1/inventory/network",
        json=payload,
        headers=auth_headers
    )
    assert post_resp.status_code == 200
    res_data = post_resp.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) == 2

    # Verify database directly
    stmt = select(NetworkAdapterInventory).where(NetworkAdapterInventory.endpoint_id == endpoint_id)
    db_res = await db_session.execute(stmt)
    db_records = db_res.scalars().all()
    assert len(db_records) == 2
    
    db_map = {r.interface_guid: r for r in db_records}
    assert adapter_guid_1 in db_map
    assert db_map[adapter_guid_1].mac_address == "00:11:22:33:44:55"

    # 5. Incremental Reconciliation test
    # We upload adapter 1 updated, remove adapter 2, and add new adapter 3
    adapter_guid_3 = str(uuid.uuid4())
    payload_reconcile = [
        {
            # Updated adapter 1
            "hostname": "TEST-NET-HOST",
            "domain_workgroup": "WORKGROUP",
            "adapter_name": "Ethernet Adapter 1",
            "adapter_description": "Intel(R) Ethernet Connection I219-LM",
            "interface_guid": adapter_guid_1,
            "mac_address": "00:11:22:33:44:55",
            "ipv4": "192.168.1.200",  # Updated IP
            "ipv6": "fe80::11",
            "subnet_mask": "255.255.255.0",
            "gateway": "192.168.1.1",
            "dns_servers": "1.1.1.1",
            "dhcp_enabled": True,
            "dhcp_server": "192.168.1.1",
            "lease_obtained": "2026-07-29T10:00:00Z",
            "lease_expires": "2026-07-30T10:00:00Z",
            "interface_speed": 1000000000,
            "interface_type": "Ethernet",
            "operational_status": "Connected",
            "is_physical": True,
            "connection_type": "Ethernet",
            "is_vpn": False
        },
        {
            # New adapter 3
            "hostname": "TEST-NET-HOST",
            "domain_workgroup": "WORKGROUP",
            "adapter_name": "VPN Tunnel",
            "adapter_description": "WireGuard Tunnel",
            "interface_guid": adapter_guid_3,
            "mac_address": None,
            "ipv4": "10.0.0.5",
            "ipv6": "fd00::5",
            "subnet_mask": "255.255.255.255",
            "gateway": "0.0.0.0",
            "dns_servers": "10.0.0.1",
            "dhcp_enabled": False,
            "dhcp_server": "0.0.0.0",
            "lease_obtained": "",
            "lease_expires": "",
            "interface_speed": 100000000,
            "interface_type": "Virtual",
            "operational_status": "Connected",
            "is_physical": False,
            "connection_type": "Ethernet",
            "is_vpn": True
        }
    ]

    post_rec = await client.post(
        "/api/v1/inventory/network",
        json=payload_reconcile,
        headers=auth_headers
    )
    assert post_rec.status_code == 200

    # Query DB and verify reconciliation (2 records: updated adapter 1 and new adapter 3. Adapter 2 should be deleted!)
    stmt_rec = select(NetworkAdapterInventory).where(NetworkAdapterInventory.endpoint_id == endpoint_id)
    db_res_rec = await db_session.execute(stmt_rec)
    db_records_rec = db_res_rec.scalars().all()
    assert len(db_records_rec) == 2
    
    db_map_rec = {r.interface_guid: r for r in db_records_rec}
    assert adapter_guid_1 in db_map_rec
    assert db_map_rec[adapter_guid_1].ipv4 == "192.168.1.200"  # Verified update!
    assert adapter_guid_3 in db_map_rec
    assert db_map_rec[adapter_guid_3].is_vpn is True  # Verified insert!
    assert adapter_guid_2 not in db_map_rec  # Verified delete!

    # 6. GET self network inventory
    get_resp = await client.get(
        "/api/v1/inventory/network",
        headers=auth_headers
    )
    assert get_resp.status_code == 200
    assert len(get_resp.json()["data"]) == 2

    # 7. GET other endpoint network inventory by ID
    get_by_id_resp = await client.get(
        f"/api/v1/inventory/network/{endpoint_id}",
        headers=auth_headers
    )
    assert get_by_id_resp.status_code == 200
    assert len(get_by_id_resp.json()["data"]) == 2

    # 8. Access without auth header returns 401
    unauth_resp = await client.get("/api/v1/inventory/network")
    assert unauth_resp.status_code == 401
