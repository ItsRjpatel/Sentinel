import pytest
import httpx
from pathlib import Path
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager

@pytest.mark.asyncio
async def test_enrollment_workflow_success(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    client = AgentHTTPClient(base_url="http://mock-api")
    
    # Mock successful server registration response
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/endpoints/enroll"
        return httpx.Response(
            201, 
            json={
                "success": True,
                "message": "Enrolled",
                "data": {
                    "agent_id": "test-agent-uuid-456",
                    "access_token": "mock-access-token",
                    "refresh_token": "mock-refresh-token"
                }
            }
        )
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    manager = EnrollmentManager(client=client, storage=storage)
    
    # Not registered initially
    assert await manager.is_enrolled() is False
    
    # Run enrollment
    agent_id = await manager.enroll()
    assert agent_id == "test-agent-uuid-456"
    assert await manager.is_enrolled() is True
    
    # Tokens should be persisted securely
    tokens = await storage.read("tokens")
    assert tokens["access_token"] == "mock-access-token"
    assert tokens["refresh_token"] == "mock-refresh-token"
    
    # Identity must cache the agent_uuid
    identity = await storage.read("identity")
    assert identity["agent_uuid"] == "test-agent-uuid-456"
    
    # Second enrollment should hit cache and not make HTTP calls
    # Changing MockTransport handler to fail if called
    def fail_handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("Network should not be reached when cached.")
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(fail_handler)
    )
    
    cached_id = await manager.enroll()
    assert cached_id == "test-agent-uuid-456"
    await client.close()
