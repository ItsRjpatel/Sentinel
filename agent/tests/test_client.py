import pytest
import httpx
from agent.communication.client import AgentHTTPClient

@pytest.mark.asyncio
async def test_client_header_injection():
    def mock_handler(request: httpx.Request) -> httpx.Response:
        # Assert trace headers are present
        assert "X-Request-ID" in request.headers
        assert "X-Correlation-ID" in request.headers
        assert request.headers["Authorization"] == "Bearer test-jwt-token"
        return httpx.Response(200, json={"success": True})

    client = AgentHTTPClient(base_url="http://mock-api")
    # Swap out the inner client's transport with MockTransport
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    resp = await client.request(
        method="POST",
        path="/endpoints/enroll",
        json_data={"data": "test"},
        auth_token="test-jwt-token"
    )
    
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    await client.close()

@pytest.mark.asyncio
async def test_client_retry_on_server_error():
    calls = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) < 3:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(200, json={"success": True})

    # Set base_url, timeout, and max_retries = 3
    client = AgentHTTPClient(base_url="http://mock-api", max_retries=3)
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    # We expect it to succeed on the 3rd attempt after two 500 errors
    resp = await client.request(method="GET", path="/endpoints/health")
    assert resp.status_code == 200
    assert len(calls) == 3
    await client.close()
