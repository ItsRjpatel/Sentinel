# CHAPTER 3: REQUIREMENTS ANALYSIS

## 3.1 Functional Requirements
- **Endpoint Enrollment**: Endpoints must securely authenticate and register with the backend using a unique enrollment secret.
- **Inventory Collection**: The agent must periodically collect Hardware, OS, Network, Storage, and Software data.
- **Real-Time Telemetry**: The agent must stream CPU and memory utilization at predefined intervals.
- **Alerting Engine**: The backend must evaluate telemetry and trigger alerts (e.g., HIGH_MEMORY) when utilization exceeds 90%.
- **Command Orchestration**: Administrators must be able to dispatch commands (e.g., lush_dns) to targeted endpoints.
- **Notification System**: The system must notify administrators via the UI when new alerts are generated.

## 3.2 Non-Functional Requirements
- **Scalability**: The backend must support concurrent connections using asynchronous processing.
- **Security**: All API communication must be secured via HTTPS. Agent identities must be encrypted locally using DPAPI.
- **Performance**: The agent footprint should be minimal, utilizing built-in Windows APIs (WMI) rather than launching heavy external processes.
- **Reliability**: The agent must run persistently as a Windows Service and automatically reconnect upon network failure.

## 3.3 Hardware Requirements
- **Agent**: Minimum 1GHz Processor, 512MB RAM, 100MB Disk Space.
- **Backend Server**: Minimum 1 vCPU, 1GB RAM (Render free/starter tier equivalent).

## 3.4 Software Requirements
- **Agent OS**: Windows 10/11 or Windows Server 2016/2019/2022.
- **Backend**: Python 3.14+, PostgreSQL 14+.
- **Frontend**: Modern web browser (Chrome, Edge, Firefox).

## 3.5 System Constraints
- The agent is currently restricted to the Windows Operating System due to reliance on WMI, PowerShell, and DPAPI.

## 3.6 Assumptions
- Target endpoints have internet connectivity to reach the centralized backend.
- Administrators have sufficient privileges to install the agent service on endpoints.
