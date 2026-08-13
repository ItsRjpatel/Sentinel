# DIAGRAM 1: SYSTEM ARCHITECTURE

**Purpose**: Demonstrates the three-tier high-level architecture of Endpoint Sentinel X.

`mermaid
graph TD
    A[Windows Endpoint Agent] -->|HTTPS / WSS| B[FastAPI Backend]
    B --> C[(PostgreSQL Database)]
    D[React Admin Dashboard] -->|HTTPS / WSS| B
    
    subgraph Endpoint
    A1[Hardware Collector] --> A
    A2[OS Collector] --> A
    A3[Task Scheduler] --> A
    end
    
    subgraph Cloud Server
    B1[REST API] --> B
    B2[WebSocket Manager] --> B
    B3[Alert Engine] --> B
    end
`
