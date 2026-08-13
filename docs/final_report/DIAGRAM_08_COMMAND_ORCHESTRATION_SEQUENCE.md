# DIAGRAM 8: COMMAND ORCHESTRATION SEQUENCE

**Purpose**: Shows how commands are queued and executed asynchronously.

`mermaid
sequenceDiagram
    participant Admin as React UI
    participant Backend as FastAPI Server
    participant Agent as Windows Agent

    Admin->>Backend: POST /commands/queue (command="flush_dns")
    Backend-->>Admin: Command ID (Status: pending)
    
    Agent->>Backend: POST /telemetry/heartbeat
    Backend-->>Agent: Response includes pending Command ID
    
    Agent->>Agent: Execute locally
    Agent->>Backend: POST /commands/{id}/result (output)
    Backend->>Admin: WebSocket Notification (Command Complete)
`
