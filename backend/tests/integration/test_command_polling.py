import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from app.modules.commands.enums import CommandStatus, CommandType
from app.modules.auth.models import User
from app.modules.endpoints.models import Endpoint
from app.core.security import create_access_token

@pytest.fixture
async def admin_user(db_session):
    stmt = select(User).where(User.username == "admin")
    res = await db_session.execute(stmt)
    admin = res.scalar_one_or_none()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin_cmd_poll@example.com",
            password_hash="fake-hash",
            is_active=True,
            is_verified=True
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)
    return admin

@pytest.fixture
async def test_endpoint(db_session):
    endpoint_id = uuid.uuid4()
    endpoint = Endpoint(
        id=endpoint_id,
        agent_id=str(uuid.uuid4()),
        hostname="TEST-POLL-HOST",
        os_version="Windows 11",
        hardware_hash="fake-hash-poll",
        status="healthy"
    )
    db_session.add(endpoint)
    await db_session.commit()
    await db_session.refresh(endpoint)
    return endpoint

@pytest.fixture
def agent_auth_headers(test_endpoint):
    # Agent authentication uses the endpoint_id as subject
    token = create_access_token(subject=str(test_endpoint.id), username=test_endpoint.hostname, roles=[])
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(admin_user):
    token = create_access_token(subject=str(admin_user.id), username=admin_user.username, roles=["admin"])
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_poll_no_command(client: AsyncClient, db_session, test_endpoint, agent_auth_headers):
    # Polling when there are no commands should return 204 No Content
    response = await client.get("/api/v1/commands/poll", headers=agent_auth_headers)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_poll_one_command_becomes_sent(client: AsyncClient, db_session, test_endpoint, admin_auth_headers, agent_auth_headers):
    # 1. Admin queues a command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.PING.value
    }
    create_resp = await client.post("/api/v1/commands", json=payload, headers=admin_auth_headers)
    assert create_resp.status_code == 201
    command_id = create_resp.json()["command_id"]

    # 2. Agent polls and receives the command
    poll_resp = await client.get("/api/v1/commands/poll", headers=agent_auth_headers)
    assert poll_resp.status_code == 200
    command_data = poll_resp.json()
    assert command_data["id"] == command_id
    assert command_data["status"] == CommandStatus.SENT.value
    assert command_data["command_type"] == CommandType.PING.value

    # 3. Agent polls again, should receive 204 since the command is already SENT
    poll_resp2 = await client.get("/api/v1/commands/poll", headers=agent_auth_headers)
    assert poll_resp2.status_code == 204
