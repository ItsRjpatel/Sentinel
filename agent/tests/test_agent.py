import pytest
import asyncio
import httpx
from pathlib import Path
from agent.utils.container import Container
from agent.communication.client import AgentHTTPClient
from agent.main import async_service_start

@pytest.mark.asyncio
async def test_agent_bootstrap_and_execution(tmp_path, monkeypatch):
    # Set environments variables to point config to our temporary folder
    monkeypatch.setenv("SENTINEL_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SENTINEL_SERVER_URL", "http://mock-api")
    monkeypatch.setenv("SENTINEL_HEARTBEAT_INTERVAL_SECONDS", "1")
    
    calls = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path == "/endpoints/enroll":
            return httpx.Response(201, json={
                "success": True,
                "data": {
                    "agent_id": "test-agent-id-999",
                    "access_token": "bootstrap-access-token",
                    "refresh_token": "bootstrap-refresh-token"
                }
            })
        if request.url.path == "/endpoints/heartbeat":
            return httpx.Response(200, json={"success": True})
        return httpx.Response(404)

    # Monkeypatch AgentHTTPClient.__init__ to inject MockTransport
    orig_init = AgentHTTPClient.__init__
    def mock_client_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            transport=httpx.MockTransport(mock_handler)
        )
    
    monkeypatch.setattr(AgentHTTPClient, "__init__", mock_client_init)

    # Start the service task in background
    bootstrap_task = asyncio.create_task(async_service_start())
    
    # Let it run for 1.5 seconds to enroll and trigger first heartbeat
    await asyncio.sleep(1.5)
    
    # Assert Container values are correctly bound (Dependency Injection validation)
    container = Container.get_instance()
    assert container.config is not None
    assert container.storage is not None
    assert container.http_client is not None
    assert container.enrollment_service is not None
    assert container.heartbeat_service is not None
    assert container.scheduler is not None
    
    # Verify enrollment and heartbeat API paths were requested
    assert "/endpoints/enroll" in calls
    assert "/endpoints/heartbeat" in calls
    
    # Trigger SCM stop event
    from agent.main import _stop_event
    assert _stop_event is not None
    _stop_event.set()
    
    # Wait for loop to shutdown gracefully
    await bootstrap_task
