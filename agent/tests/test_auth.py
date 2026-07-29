import pytest
import httpx
from pathlib import Path
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.communication.client import AgentHTTPClient

@pytest.mark.asyncio
async def test_auto_token_injection(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    # Seed initial tokens
    await storage.write("tokens", {
        "access_token": "seed-access-token",
        "refresh_token": "seed-refresh-token"
    })
    
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    # Assert Authorization header uses seed token
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer seed-access-token"
        return httpx.Response(200, json={"success": True})
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    resp = await client.request(method="GET", path="/endpoints/me")
    assert resp.status_code == 200
    await client.close()

@pytest.mark.asyncio
async def test_auto_token_rotation_on_401(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    await storage.write("tokens", {
        "access_token": "expired-access-token",
        "refresh_token": "valid-refresh-token"
    })
    
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    calls = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        
        # 1st call: request endpoints/me with expired token
        if len(calls) == 1:
            assert request.headers["Authorization"] == "Bearer expired-access-token"
            return httpx.Response(401, text="Unauthorized")
            
        # 2nd call: token refresh request
        if len(calls) == 2:
            assert request.url.path == "/auth/refresh"
            import json
            req_data = json.loads(request.content.decode("utf-8"))
            assert req_data == {"refresh_token": "valid-refresh-token"}
            return httpx.Response(200, json={
                "success": True,
                "data": {
                    "access_token": "new-access-token",
                    "refresh_token": "new-refresh-token"
                }
            })
            
        # 3rd call: retried endpoints/me request
        if len(calls) == 3:
            assert request.headers["Authorization"] == "Bearer new-access-token"
            return httpx.Response(200, json={"success": True})
            
        return httpx.Response(500)
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    resp = await client.request(method="GET", path="/endpoints/me")
    assert resp.status_code == 200
    assert len(calls) == 3
    
    # Assert tokens were updated on disk
    updated_tokens = await storage.read("tokens")
    assert updated_tokens["access_token"] == "new-access-token"
    assert updated_tokens["refresh_token"] == "new-refresh-token"
    await client.close()
