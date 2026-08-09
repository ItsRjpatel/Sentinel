# Chapter 4. Requirement Analysis

## 4.1 Introduction
Requirement analysis defines the expectations of the users and the constraints under which the system must operate. This chapter specifies the functional and non-functional requirements for Endpoint Sentinel X, establishing the baseline against which the system’s success is evaluated.

## 4.2 Functional Requirements
Functional requirements define the core behaviors and features the system must implement.
1.  **Agent Enrollment:** The system must allow administrators to generate secure enrollment scripts or installers that register a new Windows endpoint with the central server and establish cryptographic trust (JWT).
2.  **Inventory Collection:** The agent must automatically collect and upload hardware specifications (CPU, RAM, Disks), network adapter details, installed software, and active Windows services.
3.  **Live Console:** The system must provide a secure, browser-based interactive terminal that connects directly to a specific endpoint's shell via WebSockets.
4.  **Remote Commands:** Administrators must be able to dispatch asynchronous PowerShell or CMD commands to endpoints. The system must record the command, its execution status, and the standard output/error streams.
5.  **Dashboard Analytics:** The web interface must present global metrics, including the total number of enrolled endpoints, online/offline status, and recent security or system alerts.
6.  **Role-Based Access Control (RBAC):** The system must enforce access controls, ensuring that only authorized administrators can view telemetry or execute remote commands.

## 4.3 Non-Functional Requirements
Non-functional requirements specify the quality attributes, performance goals, and security constraints of the system.
1.  **Scalability:** The backend must be capable of maintaining concurrent WebSocket connections and processing frequent heartbeat requests without significant degradation in response times.
2.  **Security:** All communication between the agent, backend, and frontend must be encrypted using TLS (HTTPS/WSS). Authentication must rely on secure JSON Web Tokens (JWT) with appropriately configured expiration times.
3.  **Reliability:** The Windows agent must operate as a resilient background service. It must automatically recover from transient network failures and securely resume telemetry transmission once connectivity is restored.
4.  **Low Latency:** The Live Console feature must strive for near real-time responsiveness, minimizing the delay between a user's keystroke in the browser and the execution on the remote endpoint.
5.  **Usability:** The web frontend must offer a clean, intuitive, and highly responsive user interface, adhering to modern design principles (e.g., dark mode, responsive layouts).

## 4.4 Hardware Requirements
### 4.4.1 Backend Server (Minimum Prototype Specs)
*   **CPU:** 2 vCPU Cores
*   **Memory:** 4 GB RAM
*   **Storage:** 20 GB SSD (excluding long-term database storage)
*   **Network:** 1 Gbps Interface

### 4.4.2 Windows Endpoint (Agent)
*   **CPU:** 1 GHz Processor or faster
*   **Memory:** 512 MB RAM
*   **Storage:** 100 MB available disk space
*   **Network:** Active Internet/Intranet connection

## 4.5 Software Requirements
### 4.5.1 Backend and Database
*   **Operating System:** Linux (Ubuntu 22.04 LTS recommended) or containerized via Docker.
*   **Runtime:** Python 3.10 or higher.
*   **Database:** PostgreSQL 15 or higher.
*   **Frameworks:** FastAPI, SQLAlchemy 2.0, Uvicorn, Alembic.

### 4.5.2 Windows Endpoint
*   **Operating System:** Windows 10, Windows 11, or Windows Server 2016/2019/2022.
*   **Dependencies:** None (The agent is compiled into a standalone standalone executable via PyInstaller, containing its own Python runtime).

### 4.5.3 Frontend Client (Administrator)
*   **Browser:** Modern WebSocket-compatible web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari).
*   **Runtime (Development):** Node.js 18+ and npm/yarn/pnpm.
*   **Frameworks:** React 18, Vite, Tailwind CSS.

## 4.6 Network Requirements
*   **Port 443 (HTTPS/WSS):** Must be open outbound from the Windows endpoints to the centralized backend server.
*   **Port 443 / 80:** Must be open inbound on the centralized backend server to accept agent telemetry and administrator web traffic.
*   **Internal Database Port (5432):** Must be accessible by the FastAPI backend server to communicate with the PostgreSQL instance.
