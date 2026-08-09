import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.auth.models import User
from app.modules.endpoints.models import Endpoint
from app.modules.commands.models import Command
from app.modules.commands.enums import CommandStatus, CommandType

@pytest.fixture
async def setup_command_test_data(db_session: AsyncSession):
    # Create test user
    user = User(
        username="cmd_result_test",
        email="cmd_result@example.com",
        password_hash="test",
        is_active=True
    )
    db_session.add(user)

    # Create test endpoint
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        agent_id=str(uuid.uuid4()),
        hostname="test-cmd-result-ep",
        os_version="Windows 10",
        hardware_hash="dummy_hash_123",
        mac_addresses=["AA:BB:CC:DD:EE:GG"],
        ip_addresses=["192.168.1.5"],
        status="active"
    )
    db_session.add(endpoint)
    await db_session.commit()
    await db_session.refresh(endpoint)

    return {"user": user, "endpoint": endpoint}

@pytest.mark.asyncio
async def test_upload_command_result_success(client: AsyncClient, db_session: AsyncSession, setup_command_test_data):
    # Setup
    endpoint = setup_command_test_data["endpoint"]
    
    # Create a command in SENT status
    command = Command(
        endpoint_id=endpoint.id,
        command_type=CommandType.PING.value,
        status=CommandStatus.SENT.value
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)
    
    # Note: Agent auth uses tokens where subject is the endpoint ID.
    from app.core.security import create_access_token
    token = create_access_token(subject=str(endpoint.id), username="agent", roles=[])
    
    # Upload result
    response = await client.post(
        f"/api/v1/commands/{command.id}/result",
        json={
            "success": True,
            "duration_ms": 150,
            "result": {"hostname": "test"},
            "error": None
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["result"] == {"hostname": "test"}
    assert data["error_message"] is None
    
    # Verify DB
    stmt = select(Command).where(Command.id == command.id)
    res = await db_session.execute(stmt)
    db_cmd = res.scalar_one()
    assert db_cmd.status == "SUCCESS"
    assert db_cmd.completed_at is not None

@pytest.mark.asyncio
async def test_upload_command_result_failure(client: AsyncClient, db_session: AsyncSession, setup_command_test_data):
    endpoint = setup_command_test_data["endpoint"]
    
    # Create a command in RUNNING status
    command = Command(
        endpoint_id=endpoint.id,
        command_type=CommandType.PING.value,
        status=CommandStatus.RUNNING.value
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)
    
    from app.core.security import create_access_token
    token = create_access_token(subject=str(endpoint.id), username="agent", roles=[])
    
    # Upload failure result
    response = await client.post(
        f"/api/v1/commands/{command.id}/result",
        json={
            "success": False,
            "duration_ms": 500,
            "result": None,
            "error": "Failed to connect"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert data["error_message"] == "Failed to connect"
    
@pytest.mark.asyncio
async def test_upload_command_result_invalid_status(client: AsyncClient, db_session: AsyncSession, setup_command_test_data):
    endpoint = setup_command_test_data["endpoint"]
    
    # Create a command in PENDING status (not sent yet)
    command = Command(
        endpoint_id=endpoint.id,
        command_type=CommandType.PING.value,
        status=CommandStatus.PENDING.value
    )
    db_session.add(command)
    await db_session.commit()
    await db_session.refresh(command)
    
    from app.core.security import create_access_token
    token = create_access_token(subject=str(endpoint.id), username="agent", roles=[])
    
    # Upload result
    response = await client.post(
        f"/api/v1/commands/{command.id}/result",
        json={
            "success": True,
            "duration_ms": 100,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "Cannot update result" in response.json()["detail"]
