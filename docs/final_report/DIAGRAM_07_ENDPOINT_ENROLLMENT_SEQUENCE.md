# DIAGRAM 7: ENDPOINT ENROLLMENT SEQUENCE

**Purpose**: Details the secure enrollment handshake.

`mermaid
sequenceDiagram
    participant Installer as Agent Installer
    participant Agent as Windows Service
    participant Backend as FastAPI Server
    participant DB as PostgreSQL

    Installer->>Backend: POST /endpoints/enroll (Token)
    Backend->>DB: Verify & Save Endpoint
    Backend-->>Installer: JWT Access & Refresh Tokens
    Installer->>Agent: Save Tokens via DPAPI
    Installer->>Agent: Start NSSM Service
    Agent->>Backend: POST /inventory/hardware
`
