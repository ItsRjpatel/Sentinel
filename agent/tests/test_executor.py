import pytest
from agent.commands.executor import CommandExecutor

@pytest.fixture
def executor():
    return CommandExecutor()

def test_ping_command(executor):
    command = {"command_id": "test-ping-1", "command_type": "PING"}
    result = executor.execute(command)
    assert result["success"] is True
    assert result["command_id"] == "test-ping-1"
    assert "hostname" in result["result"]
    assert "time" in result["result"]

def test_unknown_command(executor):
    command = {"command_id": "test-unknown-1", "command_type": "UNKNOWN_CMD"}
    result = executor.execute(command)
    assert result["success"] is False
    assert result["command_id"] == "test-unknown-1"
    assert "Unknown command type" in result["error"]

def test_get_process_list(executor):
    command = {"command_id": "test-proc-1", "command_type": "GET_PROCESS_LIST"}
    result = executor.execute(command)
    assert result["success"] is True
    assert isinstance(result["result"]["processes"], list)
    assert len(result["result"]["processes"]) > 0
    # verify schema
    proc = result["result"]["processes"][0]
    assert "pid" in proc
    assert "name" in proc
    assert "cpu" in proc
    assert "memory_mb" in proc

def test_get_service_list(executor):
    command = {"command_id": "test-svc-1", "command_type": "GET_SERVICE_LIST"}
    result = executor.execute(command)
    assert result["success"] is True
    assert isinstance(result["result"]["services"], list)
    if len(result["result"]["services"]) > 0:
        svc = result["result"]["services"][0]
        assert "name" in svc
        assert "display_name" in svc
        assert "status" in svc

def test_restart_service_invalid(executor):
    command = {
        "command_id": "test-rest-1", 
        "command_type": "RESTART_SERVICE",
        "payload": {"service_name": "invalid&name"}
    }
    result = executor.execute(command)
    assert result["success"] is False
    assert "Invalid or missing" in result["result"]["error"]
