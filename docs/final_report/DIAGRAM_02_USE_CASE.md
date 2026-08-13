# DIAGRAM 2: USE CASE DIAGRAM

**Purpose**: Identifies the primary actors and their interactions with the system.

`mermaid
usecaseDiagram
    actor Administrator as Admin
    actor WindowsEndpoint as Endpoint

    Admin --> (View Dashboard)
    Admin --> (Execute Remote Command)
    Admin --> (View Alerts)
    
    Endpoint --> (Enroll Agent)
    Endpoint --> (Submit Telemetry)
    Endpoint --> (Poll Commands)
`
*(Note: Mermaid usecase syntax is not natively supported in all viewers, standard flowchart can represent this if needed)*

`mermaid
graph LR
    A[Administrator] --> B(View Dashboard)
    A --> C(Execute Command)
    A --> D(View Alerts)
    
    E[Windows Endpoint] --> F(Enroll Agent)
    E --> G(Submit Telemetry)
    E --> H(Receive & Execute Command)
`
