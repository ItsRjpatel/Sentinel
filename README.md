<div align="center">
  <img src="https://img.icons8.com/?size=100&id=42749&format=png&color=000000" alt="Sentinel Logo" width="80"/>
  <h1>Endpoint Sentinel X</h1>
  <p><strong>Enterprise Endpoint Monitoring & Management Platform</strong></p>
  <p>
    <img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.13+-blue?logo=python&logoColor=white">
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.141.1-009688?logo=fastapi&logoColor=white">
    <img alt="React" src="https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=black">
  </p>
</div>

---

## 1. Project Overview

**Endpoint Sentinel X** is a modern, full-stack Enterprise Endpoint Management Platform designed to solve the complex challenge of managing, monitoring, and securing distributed workstation and server fleets.

In modern enterprise environments, IT administrators and security teams need deep visibility into endpoint health, hardware configurations, and active security threats. Similar to platforms like **Microsoft Intune** or **ManageEngine Endpoint Central**, Endpoint Sentinel X provides centralized remote administration, real-time telemetry streaming, and automated patch/command orchestration. 

It provides an integrated "single pane of glass" for both IT Operations (inventory, software, OS metrics) and Security Operations (alerts, endpoint isolation, security posture scoring).

### 🚀 Live Demo

*Note: Services may be placed into sleep/hibernation mode or activated only during demonstrations to conserve cloud resources. If the links are inaccessible, please reach out for an active demo.*

- **Frontend Application:** [https://sentinel-web-dl5o.onrender.com](https://sentinel-web-dl5o.onrender.com)
- **Backend API (Swagger):** [https://sentinel-backend-x.azurewebsites.net/docs](https://sentinel-backend-x.azurewebsites.net/docs)

---

## 2. Features

*Note: All features listed below are actively implemented in the current codebase.*

*   **Role-Based Access Control & Authentication:** Secure JWT-based authentication with strict role assignments (Super Admin, Security Analyst, Operator, Viewer) governing access to specific API endpoints.
*   **Automated Endpoint Enrollment:** PowerShell-driven agent deployment scripts that automatically register new endpoints, exchange secure tokens, and establish bidirectional communication channels.
*   **Hardware Inventory & Telemetry:** Automated periodic collection of CPU, Memory, Disk, and Network Interface specifications.
*   **OS & Software Inventory:** Real-time visibility into Operating System versions, installed applications, and running services.
*   **Performance Monitoring:** Continuous metrics collection ensuring administrators can quickly identify resource exhaustion or anomalous behavior.
*   **Security Alerts & Incident Tracking:** Detection logic generating alerts for suspicious behaviors, coupled with a severity-based triage dashboard.
*   **Security Posture Score:** Calculated health and compliance metrics determining the overall security status of individual endpoints.
*   **Real-time WebSocket Communication:** Persistent WebSocket connections allowing the dashboard to stream real-time updates and push instant commands to agents.
*   **Command Orchestration:** Execution of remote system commands (e.g., system scans, agent updates, process termination, patch installation) directly from the dashboard.
*   **Enterprise Dashboard:** A beautiful, responsive React dashboard utilizing modern design aesthetics to visualize endpoint health, alerts, and commands.

---

## 3. Architecture

Endpoint Sentinel X operates on a microservices-inspired client-server architecture.

### **Frontend**
- **React (v18)**: The core UI library.
- **TypeScript**: Ensuring strict type safety and reducing runtime errors.
- **Vite**: High-performance frontend build tooling.
- **Tailwind CSS**: Utility-first CSS framework for rapid, responsive UI development.
- **TanStack Query (React Query)**: For efficient server-state synchronization and caching.

### **Backend**
- **FastAPI**: High-performance asynchronous Python web framework for REST and WebSocket APIs.
- **SQLAlchemy (Async)**: Asynchronous ORM for efficient database interactions.
- **Pydantic v2**: Data validation and strict schema enforcement.
- **Alembic**: Database migration management.

### **Database**
- **PostgreSQL / Neon**: The primary relational data store. Driven asynchronously via `asyncpg`.

### **Agent**
- **Windows Service**: The endpoint agent runs continuously in the background as a registered Windows Service (packaged via PyInstaller).
- **Collectors**: Pluggable modules utilizing WMI and PowerShell to extract system inventory, software, and hardware metrics.

### **Communication Layers**
- **REST API**: For standard CRUD operations, authentication, and static data retrieval.
- **WebSockets**: For persistent, bidirectional real-time communication, command dispatching, and live telemetry streaming.

---

## 4. Architecture Diagram

```mermaid
graph TD
    subgraph "Enterprise Dashboard (Frontend)"
        UI[React UI + Tailwind]
        API_CLIENT[Axios / React Query]
        WS_CLIENT[WebSocket Service]
    end

    subgraph "Sentinel X API (Backend)"
        ROUTER[FastAPI Routers]
        AUTH[Auth / RBAC Middleware]
        WS_MANAGER[WebSocket Manager]
        SERVICES[Business Logic Services]
        ORM[SQLAlchemy Async ORM]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
    end

    subgraph "Endpoint Agent (Windows)"
        AGENT_CORE[Python Agent Service]
        COLLECTORS[WMI / PS Collectors]
        WS_CLIENT_AGENT[WebSocket Client]
        HTTP_CLIENT[REST Client]
    end

    %% Connections
    UI <--> API_CLIENT
    UI <--> WS_CLIENT
    
    API_CLIENT -- "HTTPS (REST)" --> AUTH
    WS_CLIENT -- "WSS (Real-time)" --> WS_MANAGER
    
    AUTH --> ROUTER
    ROUTER --> SERVICES
    WS_MANAGER <--> SERVICES
    SERVICES <--> ORM
    ORM <--> DB

    AGENT_CORE <--> COLLECTORS
    AGENT_CORE <--> WS_CLIENT_AGENT
    AGENT_CORE <--> HTTP_CLIENT

    HTTP_CLIENT -- "HTTPS (REST)" --> AUTH
    WS_CLIENT_AGENT -- "WSS (Real-time)" --> WS_MANAGER
```

---

## 5. Deployment Documentation

### Local Development Setup
1. **Database:** Ensure PostgreSQL is running locally and set `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sentinel` in `backend/.env`.
2. **Backend:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -e .
   alembic upgrade head
   python scripts/bootstrap.py
   uvicorn app.main:app --reload
   ```
3. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Docker Deployment (Local / Self-Hosted)
The backend includes a production-ready `Dockerfile`.
```bash
docker build -t sentinel-backend .
docker run -d -p 8000:8000 --env-file backend/.env sentinel-backend
```

### Render Deployment
1. **Database:** Create a PostgreSQL database on Render or Neon.
2. **Backend:** Deploy the repository as a **Web Service** targeting the Dockerfile. Add environment variables including `DATABASE_URL` and `CORS_ORIGINS=https://your-frontend.onrender.com`.
3. **Frontend:** Deploy as a **Static Site**. Specify build command `npm run build` and publish directory `dist`. Add `VITE_API_URL=https://your-backend.onrender.com/api/v1` to Environment Variables.

### Azure App Service Deployment
The project includes fully configured GitHub Actions workflows (`.github/workflows/main_sentinel-backend-x.yml`) designed for automated CI/CD to Azure App Service using Azure Container Registries or GHCR.
- Ensure GitHub Secrets (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) are configured.
- The `startup.sh` script automatically executes Alembic migrations prior to Gunicorn boot.

---

## 6. Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production`, `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `SECRET_KEY` | Key for cryptographic signing | `your-super-secret-key` |
| `JWT_SECRET_KEY` | Key for JWT tokens | `your-jwt-secret-key` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://front.com,http://localhost:5173` |
| `BOOTSTRAP_ADMIN_PASSWORD` | Initial Super Admin password | `StrongPass123!` |

### Frontend (`frontend/.env.production`)
| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Base URL for API requests | `https://api.domain.com/api/v1` |

---

## 7. API Documentation

The backend API is entirely documented using OpenAPI/Swagger standards. 
When the backend server is running, the interactive API documentation is available at:

*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`

---

## 8. Project Structure

```text
Sentinel/
├── .github/                  # GitHub Actions CI/CD workflows
├── agent/                    # Endpoint Windows Agent source code
│   ├── collectors/           # OS/Hardware metric collectors
│   ├── gui/                  # Desktop application tray/UI
│   ├── installer/            # PyInstaller & deployment scripts
│   └── main.py               # Agent entry point
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── api/              # Route controllers
│   │   ├── core/             # Security, configuration, websockets
│   │   ├── db/               # SQLAlchemy engine & session maker
│   │   └── modules/          # Business domains (Auth, Endpoints, Alerts)
│   ├── scripts/              # Bootstrap and admin management tools
│   ├── pyproject.toml        # Backend dependencies
│   └── startup.sh            # Azure production entry point
└── frontend/                 # React Application
    ├── src/
    │   ├── assets/           # Images, icons, global CSS
    │   ├── components/       # Reusable UI components
    │   ├── features/         # Domain-specific pages and logic
    │   └── services/         # Axios API clients & WebSocket managers
    ├── index.html            # Vite entry point
    └── package.json          # Frontend dependencies
```

---

## 9. Security Considerations

*   **Password Storage:** All passwords are mathematically one-way hashed using modern strong algorithms (Argon2 / bcrypt) before database storage.
*   **Stateless Authentication:** JSON Web Tokens (JWT) are used for stateless API authorization.
*   **Role Base Access Control:** Internal API endpoints are explicitly protected by permission dependency injectors ensuring lateral movement protection.
*   **Database Migrations:** Modifying the database schema is strictly controlled via Alembic, preventing unexpected schema drifts.
*   **CORS Enforcement:** Production configurations strictly enforce Cross-Origin Resource Sharing allowing only authenticated frontends.

---

## 10. Future Roadmap

- [ ] **Cross-Platform Agents:** Expanding endpoint support to natively cover Linux (deb/rpm) and macOS endpoints.
- [ ] **Advanced Remediation:** Implementing complex playbook-driven orchestration (e.g., auto-isolate host on critical threat detection).
- [ ] **External Integrations:** Webhooks for Microsoft Teams / Slack, and SIEM forwarding (Splunk, Elastic).
- [ ] **Extended Device Telemetry:** Including USB device control, advanced network connection monitoring, and software license tracking. 
- [ ] **Machine Learning Insights:** Anomaly detection across telemetry streams to identify silent lateral movement.
