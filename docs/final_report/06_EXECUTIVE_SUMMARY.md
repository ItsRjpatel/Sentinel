# EXECUTIVE SUMMARY

**Endpoint Sentinel X** was developed to provide a centralized, secure, and scalable solution for endpoint monitoring and management. Modern IT infrastructure demands real-time visibility into endpoint health, hardware configurations, and security postures.

## Objectives Achieved
- **Real-Time Telemetry**: Deployed a lightweight Windows agent capable of capturing precise system metrics (CPU, memory, storage) and transmitting them securely via HTTP and WebSocket channels.
- **Alerting & Notification**: Implemented an automated alert evaluation engine that detects anomalies (e.g., high memory consumption) and dispatches real-time notifications to administrators.
- **Remote Orchestration**: Engineered a secure command execution pipeline allowing administrators to remotely invoke diagnostics or remediation tasks on targeted endpoints.
- **Secure Identity Management**: Integrated Windows DPAPI for localized encryption of agent identities and authentication tokens, preventing unauthorized credential exfiltration.

## Technical Foundation
The platform was built upon a modern technology stack:
- **Backend**: Python 3.14, FastAPI, SQLAlchemy, PostgreSQL.
- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Agent**: Python, WMI, Psutil, PyInstaller (for standalone executable generation), and NSSM (for Windows Service management).
- **Deployment**: Render Cloud (Backend) and local client installations.

The successful implementation and deployment of Endpoint Sentinel X validates the proposed architecture, demonstrating its readiness for enterprise application and future expansion into advanced threat hunting and automated remediation.
