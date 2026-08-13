# DIAGRAM 4: DFD LEVEL 1

**Purpose**: Breaks down the main system into primary sub-processes.

`mermaid
graph TD
    A[Agent] -->|Inventory| P1(Process Inventory)
    A -->|Heartbeat| P2(Process Telemetry)
    
    P1 --> D1[(Database)]
    P2 --> D1
    P2 --> P3(Evaluate Alerts)
    P3 --> D1
    P3 -->|WebSocket Event| Admin[Dashboard]
    
    Admin -->|Queue Command| P4(Process Commands)
    P4 --> D1
    P4 -->|Fetch Command| A
`
