# Chapter 9. Core Workflows

## 9.1 Introduction
The functionality of Endpoint Sentinel X is driven by several complex, asynchronous workflows that coordinate activity between the Windows agent, the FastAPI backend, and the React frontend. This chapter documents the technical implementation of these core workflows.

## 9.2 Enrollment and Authentication Workflow
Before an agent can upload telemetry or receive commands, it must securely enroll with the central server.
1.  **Token Generation:** The IT Administrator generates a time-limited enrollment token from the web dashboard.
2.  **Agent Initialization:** The agent is installed on the target machine with the enrollment token embedded in its configuration.
3.  **Enrollment Request:** On first startup, the agent sends a `POST` request to the backend with the token and its initial system fingerprint (hostname, OS version).
4.  **JWT Issuance:** The backend validates the token. If valid, it generates a long-lived JSON Web Token (JWT) specifically scoped to that `agent_id` and stores the new endpoint in the database.
5.  **Persistent Storage:** The agent receives the JWT and securely stores it in its local installation directory (e.g., `C:\Program Files\SentinelAgent\config.json`). All future requests include this JWT in the `Authorization: Bearer <token>` header.

## 9.3 Inventory Collection Workflow
Inventory collection is a scheduled task managed entirely by the agent, ensuring the backend is not burdened with polling thousands of machines.
1.  **Hardware Metrics:** The agent utilizes the Python `psutil` library to read CPU utilization, memory availability, and logical disk partitions.
2.  **Software and Services:** The agent utilizes Windows Management Instrumentation (WMI) queries (e.g., `SELECT * FROM Win32_Product` and `SELECT * FROM Win32_Service`) to extract deep OS-level data.
3.  **Data Serialization:** The collected data is parsed and serialized into a structured JSON payload conforming to the backend's Pydantic schemas.
4.  **Transmission:** The payload is sent via a `POST` request to the backend, which updates the respective tables (`hardware_inventory`, `software_inventory`, etc.).

## 9.4 Heartbeat Workflow
To accurately track which endpoints are currently online, the system utilizes a simple heartbeat mechanism.
1.  **Periodic Ping:** Every 60 seconds, the agent sends an empty `POST` request to the `/api/v1/endpoints/heartbeat` endpoint.
2.  **Database Update:** The backend intercepts the JWT, identifies the endpoint, and updates the `last_heartbeat` timestamp in the database to `CURRENT_TIMESTAMP`.
3.  **Frontend Calculation:** When the React dashboard fetches the endpoints list, it calculates the time difference between the server's current time and the `last_heartbeat`. If the difference is less than 3 minutes, the endpoint is displayed as **Online**; otherwise, it is marked **Offline**.

## 9.5 Service Startup and Lifecycle Workflow
The Windows agent is designed to run completely autonomously.
1.  **SCM Hook:** The compiled executable registers itself with the Windows Service Control Manager (SCM).
2.  **Boot Phase:** When the machine boots, the SCM starts the service under the `LocalSystem` account.
3.  **Thread Spawning:** The main python script spawns separate background threads for the Heartbeat loop, the Inventory loop, and the Command Polling loop.
4.  **Graceful Termination:** If an administrator manually stops the service (e.g., via `services.msc`), the agent catches the Win32 stop event, sets a global termination flag (`threading.Event`), waits for loops to finish their current cycle, and gracefully exits without leaving orphaned processes.

## 9.6 Agent Upgrade Workflow
While partially implemented in the current prototype, the foundation for self-upgrading is established.
1.  **Version Check:** During the heartbeat, the agent transmits its current `agent_version`.
2.  **Update Command:** An administrator dispatches a special `UPDATE` remote command containing a download URL for a newer executable.
3.  **Execution:** The agent downloads the new binary, spawns a detached updater script, and immediately terminates itself to release file locks (preventing `WinError 32`). The updater script replaces the binary and restarts the service.
