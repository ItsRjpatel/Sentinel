import pytest
from httpx import AsyncClient
from sqlalchemy import select
import uuid
from app.modules.commands.enums import CommandStatus, CommandType
from app.modules.auth.models import User
from app.modules.endpoints.models import Endpoint
from app.core.security import create_access_token

@pytest.fixture
async def admin_token(db_session):
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin_cmd_test@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)
        
    token = create_access_token(subject=str(admin.id), username=admin.username, roles=["admin"])
    return token

@pytest.fixture
async def test_endpoint(db_session):
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        agent_id=str(uuid.uuid4()),
        hostname="TEST-CMD-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hash-cmd",
        status="healthy"
    )
    db_session.add(endpoint)
    await db_session.commit()
    await db_session.refresh(endpoint)
    return endpoint

@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.mark.asyncio
async def test_queue_command(client: AsyncClient, db_session, test_endpoint, auth_headers):
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.RUN_INVENTORY.value
    }
    
    response = await client.post("/api/v1/commands", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == CommandStatus.PENDING.value
    assert "command_id" in data
    
    command_id = data["command_id"]
    
    # Retrieve the command
    response = await client.get(f"/api/v1/commands/{command_id}", headers=auth_headers)
    assert response.status_code == 200
    command_data = response.json()
    assert command_data["status"] == CommandStatus.PENDING.value
    assert command_data["command_type"] == CommandType.RUN_INVENTORY.value
    assert command_data["endpoint_id"] == str(test_endpoint.id)

@pytest.mark.asyncio
async def test_queue_duplicate_inventory_command(client: AsyncClient, db_session, test_endpoint, auth_headers):
    # Queue first RUN_INVENTORY command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.RUN_INVENTORY.value
    }
    response1 = await client.post("/api/v1/commands", json=payload, headers=auth_headers)
    assert response1.status_code == 201
    
    # Queue second RUN_INVENTORY command (should fail)
    response2 = await client.post("/api/v1/commands", json=payload, headers=auth_headers)
    assert response2.status_code == 409
    assert "already pending" in response2.json()["detail"]

@pytest.mark.asyncio
async def test_cancel_command(client: AsyncClient, db_session, test_endpoint, auth_headers):
    # Queue a command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.PING.value
    }
    response = await client.post("/api/v1/commands", json=payload, headers=auth_headers)
    assert response.status_code == 201
    command_id = response.json()["command_id"]
    
    # Cancel the command
    cancel_response = await client.patch(f"/api/v1/commands/{command_id}/cancel", headers=auth_headers)
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == CommandStatus.CANCELLED.value

@pytest.mark.asyncio
async def test_get_endpoint_commands(client: AsyncClient, db_session, test_endpoint, auth_headers):
    # Queue multiple commands
    for _ in range(3):
        payload = {
            "endpoint_id": str(test_endpoint.id),
            "command_type": CommandType.PING.value
        }
        await client.post("/api/v1/commands", json=payload, headers=auth_headers)
        
    response = await client.get(f"/api/v1/endpoints/{test_endpoint.id}/commands", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 3
