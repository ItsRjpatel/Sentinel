# CHAPTER 4: SYSTEM ANALYSIS AND DESIGN

## 4.1 System Overview
Endpoint Sentinel X is a three-tier distributed application. The architecture strictly isolates the data persistence layer, the backend business logic, and the user interface. The Windows agent acts as an autonomous edge client.

## 4.2 System Architecture
The overall system is designed following the principles of Hexagonal (Ports and Adapters) Architecture. Core domain logic (such as alert evaluation and command processing) is decoupled from external delivery mechanisms like HTTP routers or database ORMs.

## 4.3 Component Architecture
### 4.3.1 Agent Architecture
The agent is a modular Python application managed by NSSM (Non-Sucking Service Manager). It consists of:
- **Schedulers**: Asynchronous loops (Heartbeat, Inventory) driving periodic tasks.
- **Collectors**: Interfaces to WMI and OS modules to extract hardware, software, and security telemetry.
- **Storage**: Secure DPAPI JSON storage for persistent identity and JWT caching.

### 4.3.2 Backend Architecture
Built on FastAPI, the backend manages state via asynchronous PostgreSQL (SQLAlchemy + asyncpg). It exposes REST APIs for the React dashboard and a separate namespace for Agent communications.

### 4.3.3 Frontend Architecture
The frontend is a Single Page Application (SPA) built with React and Vite. It utilizes Tailwind CSS for styling and Axios for API communication, maintaining a persistent WebSocket connection for real-time notifications.

## 4.4 Database Architecture
The system relies on a relational database (PostgreSQL). Key entities include:
- endpoints: Stores registered agent metadata.
- hardware_inventory, os_inventory: Stores system specs.
- 	elemetry: Stores time-series CPU/memory data.
- lerts & 
otifications: Manages stateful alerts and administrative alerts.
- commands: Tracks remote execution state.

## 4.5 Communication Architecture
- **REST Communication**: Standard HTTP POST/GET methods are used for enrollment, inventory submission, and historical data retrieval.
- **WebSocket Communication**: Used for live notification delivery to the frontend administrative dashboard.

## 4.6 Security Architecture
- **Agent Identity**: Secured locally via CryptProtectData (DPAPI).
- **API Authentication**: Short-lived JWT access tokens and long-lived refresh tokens.
- **Enrollment**: Protected by a shared administrative enrollment secret.

## 4.7 Deployment Architecture
The backend and database are containerized using Docker and deployed on Render. The frontend is built into static assets. The agent is packaged into a standalone Windows executable (SentinelAgent.exe) using PyInstaller.
