# DIAGRAM 5: ENTITY RELATIONSHIP DIAGRAM

**Purpose**: Illustrates the relational database schema.

`mermaid
erDiagram
    ENDPOINTS ||--o{ TELEMETRY : submits
    ENDPOINTS ||--o{ ALERTS : triggers
    ENDPOINTS ||--o{ COMMANDS : executes
    ENDPOINTS ||--|| HARDWARE_INVENTORY : has
    ENDPOINTS ||--|| OS_INVENTORY : has

    ENDPOINTS {
        uuid id PK
        string hostname
        string agent_id
        timestamp last_seen
    }
    TELEMETRY {
        int id PK
        uuid endpoint_id FK
        float cpu_usage
        float memory_usage
        timestamp recorded_at
    }
    ALERTS {
        int id PK
        uuid endpoint_id FK
        string alert_type
        string status
    }
    COMMANDS {
        int id PK
        uuid endpoint_id FK
        string command
        string status
        string output
    }
`
