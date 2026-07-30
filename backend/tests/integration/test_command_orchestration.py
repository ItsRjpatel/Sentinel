import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.modules.commands.enums import CommandStatus, CommandType
from app.modules.commands.models import Command

def test_queue_command(client: TestClient, db: Session, test_endpoint):
    # Queue a command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.RUN_INVENTORY.value,
        "created_by": "test_user"
    }
    
    response = client.post("/api/v1/commands", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == CommandStatus.PENDING.value
    assert "command_id" in data
    
    command_id = data["command_id"]
    
    # Retrieve the command
    response = client.get(f"/api/v1/commands/{command_id}")
    assert response.status_code == 200
    command_data = response.json()
    assert command_data["status"] == CommandStatus.PENDING.value
    assert command_data["command_type"] == CommandType.RUN_INVENTORY.value
    assert command_data["endpoint_id"] == str(test_endpoint.id)

def test_queue_duplicate_inventory_command(client: TestClient, db: Session, test_endpoint):
    # Queue first RUN_INVENTORY command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.RUN_INVENTORY.value
    }
    response1 = client.post("/api/v1/commands", json=payload)
    assert response1.status_code == 201
    
    # Queue second RUN_INVENTORY command (should fail)
    response2 = client.post("/api/v1/commands", json=payload)
    assert response2.status_code == 409
    assert "already pending" in response2.json()["detail"]

def test_cancel_command(client: TestClient, db: Session, test_endpoint):
    # Queue a command
    payload = {
        "endpoint_id": str(test_endpoint.id),
        "command_type": CommandType.PING.value
    }
    response = client.post("/api/v1/commands", json=payload)
    assert response.status_code == 201
    command_id = response.json()["command_id"]
    
    # Cancel the command
    cancel_response = client.patch(f"/api/v1/commands/{command_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == CommandStatus.CANCELLED.value

def test_get_endpoint_commands(client: TestClient, db: Session, test_endpoint):
    # Queue multiple commands
    for _ in range(3):
        payload = {
            "endpoint_id": str(test_endpoint.id),
            "command_type": CommandType.PING.value
        }
        client.post("/api/v1/commands", json=payload)
        
    response = client.get(f"/api/v1/endpoints/{test_endpoint.id}/commands")
    assert response.status_code == 200
    assert len(response.json()) >= 3
