# PROJECT TABLES

## Table 4.1 - Technology Stack
| Component | Technology | Purpose |
|---|---|---|
| Backend Framework | FastAPI (Python) | High-performance async REST APIs and WebSockets |
| Database | PostgreSQL 14 | Relational data persistence |
| ORM | SQLAlchemy & Alembic | Database migrations and object mapping |
| Frontend Framework | React, Vite, Tailwind CSS | Responsive SPA dashboard |
| Agent Language | Python 3 | Cross-compatibility and rapid development |
| Agent Packaging | PyInstaller, NSSM | Standalone executable and Windows Service management |
| Telemetry Extraction | WMI, Psutil | Hardware and OS metrics collection |
| Deployment | Render, Docker | Cloud hosting and containerization |

## Table 5.2 - Database Entities (Core)
| Table Name | Description | Key Columns |
|---|---|---|
| endpoints | Managed agents | id, hostname, gent_id, status |
| 	elemetry | Time-series metrics | endpoint_id, cpu_usage, memory_usage |
| lerts | Detected anomalies | endpoint_id, lert_type, status |
| commands | Remote execution jobs | endpoint_id, command, output, status |
| users | Admin accounts | id, email, hashed_password |

## Table 5.3 - Agent Collectors
| Collector | Mechanism | Data Extracted |
|---|---|---|
| HardwareCollector | WMI (Win32_ComputerSystem) | Manufacturer, Model, Memory |
| OperatingSystemCollector | WMI (Win32_OperatingSystem) | Version, Build, Install Date |
| NetworkCollector | WMI & sockets | MAC Addresses, IP Addresses |
| StorageCollector | WMI (Win32_LogicalDisk) | Disk space, BitLocker status |
