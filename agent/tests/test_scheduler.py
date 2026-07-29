import pytest
import httpx
from pathlib import Path
from agent.utils.storage import DPAPIJSONStorageProvider
from agent.communication.client import AgentHTTPClient
from agent.communication.enrollment import EnrollmentManager
from agent.scheduler.heartbeat import HeartbeatTask

@pytest.mark.asyncio
async def test_heartbeat_loop_success(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    # Pre-seed identity config to appear enrolled
    await storage.write("identity", {
        "machine_fingerprint": "fake-fingerprint",
        "installation_id": "fake-install-id",
        "agent_uuid": "enrolled-agent-uuid"
    })
    
    called_path = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        called_path.append(request.url.path)
        return httpx.Response(200, json={"success": True})
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    enroll_manager = EnrollmentManager(client=client, storage=storage)
    task = HeartbeatTask(
        interval_seconds=1, 
        client=client, 
        storage=storage, 
        enrollment_manager=enroll_manager
    )
    
    # Execute heartbeat
    await task.execute()
    assert "/endpoints/heartbeat" in called_path
    assert task.is_online is True
    await client.close()

@pytest.mark.asyncio
async def test_heartbeat_offline_caching_and_drain(tmp_path):
    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    await storage.write("identity", {
        "machine_fingerprint": "fake-fingerprint",
        "installation_id": "fake-install-id",
        "agent_uuid": "enrolled-agent-uuid"
    })
    
    # Mock connection failures (raises ConnectError)
    def mock_fail_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Network is down")
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_fail_handler)
    )
    
    enroll_manager = EnrollmentManager(client=client, storage=storage)
    task = HeartbeatTask(
        interval_seconds=1, 
        client=client, 
        storage=storage, 
        enrollment_manager=enroll_manager
    )
    
    # Execute heartbeat (connection drops)
    await task.execute()
    assert task.is_online is False
    
    # Assert telemetry is enqueued in secure storage
    queued_data = await storage.read("telemetry_queue")
    assert queued_data is not None
    assert len(queued_data) == 1
    assert queued_data[0]["status"] == "healthy"
    
    # Restore connection
    called_path = []
    def mock_restore_handler(request: httpx.Request) -> httpx.Response:
        called_path.append(request.url.path)
        return httpx.Response(200, json={"success": True})
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_restore_handler)
    )
    
    # Execute again (restores and drains)
    await task.execute()
    assert task.is_online is True
    assert "/endpoints/heartbeat" in called_path
    
    # Assert storage queue is drained
    drained_queue = await storage.read("telemetry_queue")
    assert len(drained_queue) == 0
    await client.close()


@pytest.mark.asyncio
async def test_hardware_inventory_task_success(tmp_path):
    from agent.scheduler.hardware_task import HardwareInventoryTask
    from agent.collectors.hardware.collector import HardwareCollector

    storage = DPAPIJSONStorageProvider(base_dir=tmp_path)
    client = AgentHTTPClient(base_url="http://mock-api", storage=storage)
    
    # Pre-seed identity config to appear enrolled
    await storage.write("identity", {
        "machine_fingerprint": "fake-fingerprint",
        "installation_id": "fake-install-id",
        "agent_uuid": "enrolled-agent-uuid"
    })
    
    called_path = []
    
    def mock_handler(request: httpx.Request) -> httpx.Response:
        called_path.append(request.url.path)
        return httpx.Response(200, json={"success": True})
        
    client.client = httpx.AsyncClient(
        base_url="http://mock-api",
        transport=httpx.MockTransport(mock_handler)
    )
    
    enroll_manager = EnrollmentManager(client=client, storage=storage)
    collector = HardwareCollector()
    
    task = HardwareInventoryTask(
        interval_seconds=86400,
        client=client,
        enrollment_manager=enroll_manager,
        collector=collector
    )
    
    await task.execute()
    assert "/inventory/hardware" in called_path
    await client.close()
