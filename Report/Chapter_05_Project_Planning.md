# Chapter 5. Project Planning & Development Methodology

## 5.1 Introduction
The successful execution of a complex software engineering project requires rigorous planning, risk management, and a structured development lifecycle. This chapter outlines the Agile-inspired methodology adopted for the development of Endpoint Sentinel X, detailing the project phases, milestones, and risk mitigation strategies.

## 5.2 Development Methodology
The project was developed using an iterative, architecture-first approach modeled after Agile methodologies. The development lifecycle was divided into distinct phases, ensuring that core infrastructure was stable before building dependent features. This approach allowed for continuous integration, testing, and refinement based on intermediate results.

### 5.2.1 Iterative Phases
1.  **Phase 1: Architecture & Database Design:** Defined the entity-relationship models, initialized the PostgreSQL database using SQLAlchemy, and established Alembic migration scripts.
2.  **Phase 2: Backend API Development:** Developed the asynchronous FastAPI application, implementing JWT authentication, RBAC, and RESTful endpoints for inventory reception and command queuing.
3.  **Phase 3: Agent Development:** Engineered the Python-based Windows agent, implementing WMI collection logic, the heartbeat mechanism, and the PyInstaller compilation process to run as a Windows Service.
4.  **Phase 4: Real-Time Communication:** Implemented the complex WebSocket relay layer in both the FastAPI backend and the Windows agent to support the Live Console feature.
5.  **Phase 5: Frontend Development:** Built the React/Vite web dashboard, integrating with the REST APIs to visualize endpoint data and execute commands.
6.  **Phase 6: Integration, Testing, and Hardening:** Conducted end-to-end testing across all components, resolved concurrent execution bugs (e.g., SQLite concurrency issues replaced with PostgreSQL), and finalized UI polish.

## 5.3 Project Milestones

| Milestone | Description | Status |
| :--- | :--- | :--- |
| **M1: Foundation** | Initial repository setup, database schema creation, and basic FastAPI routing. | Completed |
| **M2: Agent Telemetry** | Windows agent successfully collecting and uploading hardware/software data to the API. | Completed |
| **M3: Remote Commands** | Asynchronous execution of PowerShell scripts via the management console. | Completed |
| **M4: Live Console** | Successful implementation of bidirectional WebSocket communication for interactive shells. | Completed |
| **M5: Installer Integration** | Custom installation wizard and stable Windows Service Control Manager (SCM) lifecycle. | Completed |
| **M6: Feature Freeze** | UI cleanup, removal of unimplemented placeholder features, and final production build. | Completed |
| **M7: Documentation** | Completion of the BITS WILP final project report and architectural documentation. | Completed |

## 5.4 Risk Management

Identifying and mitigating risks early was critical to maintaining the project timeline. The following table outlines the primary risks encountered and the mitigation strategies employed.

| Risk Category | Identified Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Technical** | WebSocket connections dropping due to intermediate proxies or NAT timeouts. | Implemented robust reconnect logic and periodic application-level ping/pong frames in the agent. |
| **Security** | Hardcoded credentials or exposed API keys during agent deployment. | Utilized dynamic, time-limited enrollment tokens and enforced JWT authentication for all subsequent communications. |
| **Deployment** | Python runtime dependencies complicating agent installation on diverse Windows versions. | Packaged the entire agent and its dependencies into a standalone executable using PyInstaller. |
| **Performance** | SQLite database locking issues under high concurrent load from multiple agents. | Migrated the primary data store from SQLite to a highly concurrent PostgreSQL database using `asyncpg`. |
| **OS Compatibility** | Windows Service lifecycle management (start/stop/restart) throwing `WinError 32` file locks. | Implemented a dedicated ServiceManager class with graceful loop teardown and graceful thread termination. |

## 5.5 Tools and Work Environment
The development was primarily conducted on a Windows 11 workstation, utilizing Visual Studio Code as the primary IDE. Git was used for version control, with the repository hosted on a local development server. Virtualized environments (Hyper-V Windows VMs) were heavily utilized to safely test agent deployment, enrollment, and remote command execution without compromising the host development machine. Database schema migrations were managed exclusively via Alembic to ensure consistency across testing and production environments.
