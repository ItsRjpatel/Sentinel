# DIAGRAM 6: DEPLOYMENT ARCHITECTURE

**Purpose**: Shows the physical deployment topology.

`mermaid
graph TD
    subgraph Corporate Network
        A[Windows 10/11 Endpoint 1]
        B[Windows Server Endpoint 2]
    end
    
    subgraph Render Cloud
        C[Docker: FastAPI Backend]
        D[(PostgreSQL 14)]
        C --- D
    end
    
    subgraph Administrator Device
        E[Web Browser: React SPA]
    end
    
    A <-->|HTTPS / WSS| C
    B <-->|HTTPS / WSS| C
    E <-->|HTTPS / WSS| C
`
