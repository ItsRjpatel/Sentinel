# Chapter 8. UML Modeling

## 8.1 Introduction
Unified Modeling Language (UML) diagrams provide a standardized way to visualize the design of a system. This chapter presents the Use Case, Component, and Sequence diagrams that define the behaviors and structural boundaries of Endpoint Sentinel X, as well as Class, Deployment, and Data Flow diagrams.

## 8.2 Use Case Diagram
The Use Case diagram identifies the primary actors interacting with the system and the distinct operations they can perform.

```mermaid
usecaseDiagram
    actor Admin as "IT Administrator"
    actor Agent as "Windows Agent"
    
    usecase Enroll as "Enroll Endpoint"
    usecase Upload as "Upload Telemetry"
    usecase View as "View Dashboard"
    usecase Dispatch as "Dispatch Command"
    usecase Execute as "Fetch/Execute Command"
    usecase Console as "Open Live Console"

    Admin --> View
    Admin --> Dispatch
    Admin --> Console
    
    Agent --> Enroll
    Agent --> Upload
    Agent --> Execute
    Agent --> Console
```
*Figure 8.1: Use Case Diagram mapping primary actors to system capabilities.*

### 8.2.1 Use Case Descriptions
*   **Enroll Endpoint:** Agent registers itself with the backend using an enrollment token.
*   **Upload Telemetry:** Agent pushes hardware, software, and service data.
*   **View Dashboard:** Administrator logs in and views global metrics.
*   **Dispatch Command:** Administrator queues a PowerShell script for a specific endpoint.
*   **Fetch/Execute Command:** Agent polls for commands, executes them locally, and uploads results.
*   **Open Live Console:** Administrator initiates a WebSocket session. Agent connects and binds its local shell to the WebSocket stream.

## 8.3 Class Diagram
The Class diagram outlines the primary object-oriented models used in the backend ORM layer.

```mermaid
classDiagram
    class Endpoint {
        +UUID id
        +String hostname
        +String os_version
        +DateTime last_heartbeat
        +enroll()
    }
    class HardwareInventory {
        +UUID id
        +String cpu_model
        +Integer ram_mb
    }
    class Command {
        +UUID id
        +String payload
        +String status
        +execute()
    }
    class User {
        +UUID id
        +String username
        +login()
    }
    
    Endpoint "1" -- "*" HardwareInventory : owns
    Endpoint "1" -- "*" Command : executes
```
*Figure 8.2: High-Level Class Diagram of Backend Models.*

## 8.4 Component Diagram
The Component diagram illustrates the structural organization of the software modules.

```mermaid
graph TD
    subgraph "Frontend Client (React)"
        AuthUI[Authentication UI]
        DashboardUI[Dashboard UI]
        ConsoleUI[Terminal UI - Xterm.js]
    end

    subgraph "Backend Server (FastAPI)"
        AuthRouter[Auth Router]
        EndpointRouter[Endpoint Router]
        CommandRouter[Command Router]
        WebSocketMgr[WebSocket Manager]
    end

    subgraph "Windows Agent (Python)"
        ServiceMgr[Service Manager]
        Collector[WMI/PSutil Collector]
        CmdHandler[Command Handler]
        WSClient[WebSocket Client]
    end

    AuthUI --> AuthRouter
    DashboardUI --> EndpointRouter
    DashboardUI --> CommandRouter
    ConsoleUI -.-> WebSocketMgr
    
    Collector --> EndpointRouter
    CmdHandler --> CommandRouter
    WSClient -.-> WebSocketMgr
```
*Figure 8.3: Component Diagram highlighting module separation (To be rendered in Draw.io)*

## 8.5 Package Diagram
The Package diagram depicts the high-level directories and module groupings.

```mermaid
graph TD
    subgraph "Sentinel X Monorepo"
        pkg_frontend["Frontend (React)"]
        pkg_backend["Backend (FastAPI)"]
        pkg_agent["Agent (Python)"]
    end
    pkg_frontend -.-> pkg_backend
    pkg_agent -.-> pkg_backend
```
*Figure 8.4: Package Diagram.*

## 8.6 Deployment Diagram
The Deployment diagram shows the physical/logical nodes.

```mermaid
graph TD
    node_cloud["Cloud Server (Ubuntu)"]
    node_db["Managed PostgreSQL (Neon)"]
    node_win["Windows Endpoint (Win 11)"]
    
    node_cloud -- "TCP 5432" --> node_db
    node_win -- "HTTPS/WSS 443" --> node_cloud
```
*Figure 8.5: Deployment Diagram.*

## 8.7 Activity Diagram: Service Startup
When the Windows machine boots, the `SentinelAgentService` initiates a specific lifecycle:

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> VerifyAuth
    VerifyAuth --> StartThreads : Authorized
    VerifyAuth --> [*] : Unauthorized
    StartThreads --> WaitState
    WaitState --> Shutdown : Stop Signal Received
    Shutdown --> [*]
```
*Figure 8.6: Service Startup Activity Diagram.*

## 8.8 State Diagram: Remote Command
Describes the lifecycle of a command entity.

```mermaid
stateDiagram-v2
    [*] --> PENDING : Created by Admin
    PENDING --> SENT : Polled by Agent
    SENT --> RUNNING : Execution Started
    RUNNING --> COMPLETED : Execution Success
    RUNNING --> FAILED : Execution Error
    COMPLETED --> [*]
    FAILED --> [*]
```
*Figure 8.7: Command State Diagram.*

## 8.9 Sequence Diagrams

### 8.9.1 Remote Command Execution Sequence
```mermaid
sequenceDiagram
    participant Admin as IT Administrator
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Agent as Windows Agent

    Admin->>API: POST /commands (payload)
    API->>DB: INSERT into commands (status=PENDING)
    API-->>Admin: 201 Created (Command ID)
    
    loop Every 30 seconds
        Agent->>API: GET /commands/pending
        API-->>Agent: Returns PENDING commands
    end
    
    Agent->>API: PUT /commands/{id}/status (status=RUNNING)
    Note over Agent: Spawns subprocess (powershell.exe)
    Agent->>API: PUT /commands/{id}/results (status=COMPLETED, output)
    API->>DB: UPDATE commands
```
*Figure 8.8: Remote Command Execution Sequence Diagram*

### 8.9.2 Live Console WebSocket Sequence
```mermaid
sequenceDiagram
    participant Admin as IT Administrator
    participant API as WebSocket Manager
    participant Agent as Windows Agent

    Admin->>API: Initiates WSS connection (/ws/console/client/{id})
    API-->>Admin: Connection Established
    
    API->>Agent: Send Control Message: "START_SESSION" (via long-polling or push)
    Agent->>API: Initiates WSS connection (/ws/console/agent/{id})
    API-->>Agent: Connection Established
    
    Note over API: API now bridges Client and Agent sockets
    
    Admin->>API: types "ipconfig"
    API->>Agent: passes "ipconfig"
    Note over Agent: Writes to stdin of cmd.exe
    Note over Agent: Reads stdout of cmd.exe
    Agent->>API: returns terminal output
    API->>Admin: renders terminal output in Xterm.js
```
*Figure 8.9: Live Console WebSocket Sequence Diagram*

## 8.10 Data Flow Diagrams (DFD)

### 8.10.1 Level 0 (Context Diagram)
```mermaid
graph LR
    Admin["IT Administrator"]
    Agent["Windows Agent"]
    System(("Endpoint Sentinel X"))
    
    Admin -- "Manage endpoints, View Data" --> System
    System -- "Dashboard UI, Output" --> Admin
    
    Agent -- "Telemetry, Command Output" --> System
    System -- "Commands, Configurations" --> Agent
```
*Figure 8.10: DFD Level 0 Context Diagram.*

### 8.10.2 Level 1 DFD
```mermaid
graph TD
    Agent["Windows Agent"]
    Admin["IT Administrator"]
    
    P1(("1.0 Authentication"))
    P2(("2.0 Telemetry Processing"))
    P3(("3.0 Command Execution"))
    
    D1[("Database")]
    
    Admin --> P1
    Agent --> P1
    P1 --> D1
    
    Agent --> P2
    P2 --> D1
    
    Admin --> P3
    P3 --> D1
    D1 --> P3
    P3 --> Agent
```
*Figure 8.11: DFD Level 1 Diagram.*
