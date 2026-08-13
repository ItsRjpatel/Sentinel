# DIAGRAM 9: TELEMETRY DATA FLOW

**Purpose**: Illustrates the flow of performance metrics and alert generation.

`mermaid
graph TD
    A[Agent: psutil metrics] -->|Heartbeat POST| B(Backend: Telemetry Router)
    B --> C[(Database: Save Telemetry)]
    B --> D{Alert Service}
    D -->|>90% Memory| E(Create EndpointAlertState)
    E --> F[Generate Notification]
    F -->|WebSocket| G[Admin UI Update]
`
