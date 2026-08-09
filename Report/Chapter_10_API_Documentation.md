# Chapter 10. API Documentation

## 10.1 Introduction
The FastAPI backend exposes a comprehensive RESTful API for both the React frontend (administrative operations) and the Windows agents (telemetry and command polling). This chapter documents the critical endpoints of the system. The complete interactive documentation is available via the auto-generated Swagger UI (`/docs`).

[Screenshot Required: 21 API Documentation (Swagger)]
*Figure 10.1: FastAPI Auto-Generated Swagger Interface*

## 10.2 Administrative Endpoints (Frontend to Backend)
These endpoints require an administrative JWT generated during user login.

### 10.2.1 Get All Endpoints
*   **URL:** `/api/v1/endpoints`
*   **Method:** `GET`
*   **Authentication:** Required (Admin JWT, `Authorization: Bearer <token>`)
*   **Description:** Retrieves a paginated list of all enrolled endpoints.
*   **Validation Rules:** `skip` and `limit` query parameters must be non-negative integers.
*   **Response (200 OK):**
    ```json
    {
      "items": [
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "hostname": "DESKTOP-ABC",
          "os_version": "Windows 11",
          "last_heartbeat": "2026-08-08T10:00:00Z"
        }
      ],
      "total": 1
    }
    ```
*   **Error Codes:**
    *   `401 Unauthorized`: Invalid or missing Admin JWT.
    *   `403 Forbidden`: Insufficient RBAC permissions.
    *   `422 Unprocessable Entity`: Invalid query parameters.

### 10.2.2 Dispatch Remote Command
*   **URL:** `/api/v1/commands`
*   **Method:** `POST`
*   **Authentication:** Required (Admin JWT, `Authorization: Bearer <token>`)
*   **Description:** Queues a command for a specific endpoint.
*   **Validation Rules:** `endpoint_id` must be a valid UUID. `command_type` must be in `['POWERSHELL', 'CMD']`. `payload` cannot be empty.
*   **Request Body:**
    ```json
    {
      "endpoint_id": "123e4567-e89b-12d3-a456-426614174000",
      "command_type": "POWERSHELL",
      "payload": "Get-Process | Select-Object Name, Id"
    }
    ```
*   **Response (201 Created):** Returns the generated `command_id`.
    ```json
    {
      "id": "987e6543-e21b-34c5-b678-426614174999",
      "status": "PENDING"
    }
    ```
*   **Error Codes:**
    *   `401 Unauthorized`: Missing authentication.
    *   `403 Forbidden`: User lacks execution roles.
    *   `404 Not Found`: Target endpoint UUID does not exist.
    *   `422 Unprocessable Entity`: Payload missing or invalid command_type.

## 10.3 Agent Endpoints (Agent to Backend)
These endpoints require an agent-scoped JWT generated during enrollment.

### 10.3.1 Upload Hardware Inventory
*   **URL:** `/api/v1/inventory/hardware`
*   **Method:** `POST`
*   **Authentication:** Required (Agent JWT, `Authorization: Bearer <token>`)
*   **Validation Rules:** Memory must be > 0. Valid strings for CPU model.
*   **Request Body:**
    ```json
    {
      "cpu_model": "Intel Core i7-12700K",
      "ram_total_mb": 32768
    }
    ```
*   **Response (200 OK):** Confirmation of successful database insertion.
*   **Error Codes:**
    *   `401 Unauthorized`: Invalid agent token.
    *   `422 Unprocessable Entity`: Data type mismatch.

### 10.3.2 Fetch Pending Commands
*   **URL:** `/api/v1/commands/pending`
*   **Method:** `GET`
*   **Authentication:** Required (Agent JWT, `Authorization: Bearer <token>`)
*   **Description:** The agent polls this endpoint to retrieve scripts queued by administrators.
*   **Response (200 OK):**
    ```json
    [
      {
        "id": "987e6543-e21b-34c5-b678-426614174999",
        "command_type": "POWERSHELL",
        "payload": "ipconfig /all"
      }
    ]
    ```
*   **Error Codes:**
    *   `401 Unauthorized`: Invalid agent token.

### 10.3.3 Submit Command Results
*   **URL:** `/api/v1/commands/{command_id}/results`
*   **Method:** `PUT`
*   **Authentication:** Required (Agent JWT, `Authorization: Bearer <token>`)
*   **Validation Rules:** `command_id` must match a command assigned to this agent. `status` must be `COMPLETED` or `FAILED`.
*   **Request Body:**
    ```json
    {
      "status": "COMPLETED",
      "output": "Windows IP Configuration..."
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "message": "Command updated successfully"
    }
    ```
*   **Error Codes:**
    *   `401 Unauthorized`: Invalid agent token.
    *   `403 Forbidden`: Agent attempting to update a command belonging to a different endpoint.
    *   `404 Not Found`: Command ID does not exist.
    *   `422 Unprocessable Entity`: Invalid status string.

## 10.4 WebSocket Endpoints (Live Console)

### 10.4.1 Client Terminal Connection
*   **URL:** `ws://<server>/ws/console/client/{endpoint_id}`
*   **Authentication:** JWT required (passed via query parameter `?token=<jwt>` due to WebSocket headers limitation).
*   **Description:** The React dashboard initiates this connection. The backend holds this socket open and waits for the corresponding agent to connect.
*   **Error Codes:**
    *   `WS 1008 Policy Violation`: Invalid admin token or insufficient permissions.

### 10.4.2 Agent Shell Connection
*   **URL:** `ws://<server>/ws/console/agent/{endpoint_id}`
*   **Authentication:** Agent JWT required via query parameter.
*   **Description:** The agent initiates this connection when signaled. The backend immediately begins proxying raw byte frames between this socket and the client socket.
*   **Error Codes:**
    *   `WS 1008 Policy Violation`: Invalid agent token.
