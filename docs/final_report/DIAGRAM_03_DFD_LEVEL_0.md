# DIAGRAM 3: DFD LEVEL 0 (CONTEXT DIAGRAM)

**Purpose**: Shows the system as a single process interacting with external entities.

`mermaid
graph LR
    Admin[Administrator] -->|Command Requests| System((Endpoint Sentinel X))
    System -->|Dashboard Data| Admin
    
    Endpoint[Windows Agent] -->|Telemetry & Inventory| System
    System -->|Commands & Updates| Endpoint
`
