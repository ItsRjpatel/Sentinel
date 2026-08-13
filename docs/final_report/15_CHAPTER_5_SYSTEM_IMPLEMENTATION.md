# CHAPTER 5: SYSTEM IMPLEMENTATION

## 5.1 Endpoint Enrollment and Identity
The agent generates a unique gent_uuid and a machine_fingerprint (SHA-256 hash of BIOS UUID, CPU ID, and Motherboard Serial). This identity is registered with the backend via the /api/v1/endpoints/enroll endpoint. Authentication utilizes JWT tokens (Access and Refresh) securely stored locally using Windows DPAPI.

## 5.2 Inventory Collection
Implemented via Python's wmi and psutil libraries, the agent collects:
- **Hardware Inventory**: CPU architecture, total memory.
- **OS Inventory**: Windows version, build number, install date.
- **Network Inventory**: Adapters, IP/MAC addresses.
- **Storage/Volumes**: Disk capacities and free space.
- **Software & Services**: Installed applications and Windows Services.
- **Windows Updates**: Patch history.

## 5.3 Performance and Security Monitoring
The HeartbeatTask submits CPU and Memory metrics to the backend. Simultaneously, the agent audits security parameters, checking for unencrypted drives (BitLocker status).

## 5.4 Alerts and Duplicate Prevention
When the backend receives telemetry where Memory utilization exceeds 90%, the AlertService generates a HIGH_MEMORY alert. Duplicate alert prevention is handled using the EndpointAlertState model, which tracks the active state of an alert. Only when the condition resolves does the state reset, allowing future alerts without flooding the system.

## 5.5 Command Orchestration
The backend provides an API to queue commands (e.g., lush_dns, get_processes). The agent retrieves these via the heartbeat response, executes them using a specialized handler dictionary, and POSTs the standard output/error back to the server.

## 5.6 Agent Installer and Service
The GUI installer (built with Tkinter) accepts the Server URL and Enrollment Token. Post-enrollment, the installer configures the agent to run persistently as a Windows Service using sc.exe, ensuring it survives reboots.

## 5.7 Backend APIs and Database
FastAPI routing is separated by domain (Auth, Endpoints, Telemetry, Commands). SQLAlchemy models define the PostgreSQL schema, mapped asynchronously via syncpg.

## 5.8 React Frontend
The frontend consumes the APIs to display dashboards, detailed endpoint views, and an interactive command execution terminal. Live updates to the notification bell are powered by WebSocket events broadcasted by the backend.
