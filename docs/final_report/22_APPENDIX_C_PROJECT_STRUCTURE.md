# APPENDIX C: PROJECT STRUCTURE

`	ext
Sentinel/
├── agent/               # Windows Agent (Python)
│   ├── collectors/      # WMI/OS extraction logic
│   ├── communication/   # HTTP/WebSocket clients
│   ├── installer/       # Tkinter GUI & Service setup
│   ├── scheduler/       # Task execution loops
│   ├── security/        # DPAPI encryption & Identity
│   └── main.py          # Entry point
├── backend/             # FastAPI Server
│   ├── app/
│   │   ├── api/         # REST Routers
│   │   ├── core/        # Config & Security
│   │   ├── db/          # Alembic migrations & Models
│   │   ├── models/      # SQLAlchemy Entities
│   │   └── services/    # Business Logic (Alerts/Commands)
│   └── main.py          # Uvicorn entry point
├── frontend/            # React Dashboard
│   ├── src/
│   │   ├── components/  # UI Components
│   │   ├── pages/       # Dashboard, Endpoints, Alerts
│   │   └── services/    # Axios API client & WebSockets
├── scripts/             # Build scripts (PyInstaller)
└── docs/                # Project Documentation
`
