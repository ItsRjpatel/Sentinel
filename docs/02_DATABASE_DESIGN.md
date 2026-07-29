# Database Design

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | Database Design |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the database architecture for Sentinel.

It describes:

- Database technology
- Database standards
- Naming conventions
- Entity relationships
- Data ownership
- Indexing strategy
- Constraints
- Migration strategy
- Scalability guidelines

The database is designed to support enterprise deployments ranging from small organizations to environments managing tens of thousands of Windows endpoints.

---

# 2. Database Technology

| Component | Technology |
|------------|------------|
| Cloud Database | Neon PostgreSQL |
| Database Engine | PostgreSQL 17+ |
| ORM | SQLAlchemy 2.x (Async) |
| Driver | asyncpg |
| Migration Tool | Alembic |
| Connection Pooling | Neon Pooler |
| Database Access | SQLAlchemy Async Session |

---

# 3. Neon Database Architecture

Sentinel uses **Neon PostgreSQL** as its primary cloud database.

## Why Neon?

Neon provides a modern PostgreSQL platform with enterprise-grade capabilities while remaining easy to manage during development.

### Benefits

- Fully managed PostgreSQL
- Serverless architecture
- Automatic backups
- Database branching
- SSL enabled by default
- High availability
- Excellent SQLAlchemy compatibility
- Easy scaling
- Production ready

---

## Connection Flow

```
Application

↓

SQLAlchemy Async

↓

asyncpg Driver

↓

Neon Pooler

↓

Neon PostgreSQL
```

---

## Environment Variables

```env
DATABASE_URL=

ASYNC_DATABASE_URL=
```

---

## Development Strategy

Development uses dedicated Neon branches.

Production uses an isolated production branch.

Schema changes are managed exclusively through Alembic migrations.

Manual schema modifications are prohibited.

---

# 4. Database Design Principles

Sentinel follows the following principles.

- Normalize data whenever practical.
- Avoid duplicated information.
- Preserve historical records.
- Use UUID primary keys.
- Store timestamps in UTC.
- Enforce foreign keys.
- Use indexes on frequently queried columns.
- Never place business logic inside the database.
- Database stores data only.
- Backend owns all business rules.

---

# 5. Naming Conventions

## Tables

Plural snake_case.

Examples

```
users

roles

permissions

endpoints

alerts
```

---

## Columns

snake_case.

Examples

```
created_at

updated_at

last_seen

device_name
```

---

## Primary Keys

Every table uses

```
id UUID PRIMARY KEY
```

---

## Foreign Keys

Examples

```
user_id

endpoint_id

role_id

command_id
```

---

## Standard Timestamp Fields

```
created_at

updated_at

deleted_at
```

---

# 6. Database Modules

The database is divided into business domains.

---

## Identity

- users
- roles
- permissions
- role_permissions
- user_roles
- sessions

---

## Endpoint Management

- endpoints
- endpoint_groups
- endpoint_tags
- endpoint_status
- agent_versions

---

## Hardware Inventory

- hardware
- processors
- memory_modules
- motherboards
- bios
- graphics

---

## Operating System

- operating_systems
- windows_updates
- drivers

---

## Storage

- disks
- partitions
- volumes

---

## Network

- network_adapters
- ip_addresses
- wifi_profiles

---

## Software Inventory

- installed_software
- software_history

---

## Monitoring

- performance_metrics
- service_status
- process_metrics
- event_logs

---

## Security

- security_status
- defender_status
- firewall_status
- bitlocker_status
- secure_boot_status
- tpm_status

---

## Compliance

- compliance_policies
- compliance_results
- compliance_history

---

## Vulnerability

- vulnerabilities
- endpoint_vulnerabilities

---

## Remote Management

- commands
- command_results
- command_history

---

## Alerts

- alerts
- alert_rules
- alert_history

---

## Reports

- reports
- scheduled_reports

---

## Audit

- audit_logs
- system_events

---

# 7. Entity Relationships

```
User

↓

Role

↓

Permission

↓

System
```

```
Endpoint

↓

Inventory

↓

Monitoring

↓

Security

↓

Compliance

↓

Alerts
```

```
Administrator

↓

Command

↓

Endpoint

↓

Command Result
```

---

# 8. Inventory Design

Inventory data is separated into dedicated tables.

Example

```
Endpoint

├── Hardware

├── Operating System

├── Network

├── Storage

├── Installed Software

├── Security

└── Monitoring
```

Benefits

- Faster updates
- Smaller transactions
- Easier maintenance
- Better scalability
- Reduced duplication

---

# 9. Historical Data

Historical information is never overwritten.

Examples

- Performance History
- Security History
- Compliance History
- Alert History
- Command History
- Inventory Snapshots

Each new update creates a historical record when required.

---

# 10. Index Strategy

Indexes are created on frequently searched columns.

Examples

```
endpoint_id

user_id

hostname

status

created_at

last_seen

command_status

alert_type
```

Composite indexes are added when required after performance analysis.

---

# 11. Constraints

Database constraints include

- Primary Keys
- Foreign Keys
- NOT NULL
- UNIQUE
- CHECK Constraints

Examples

Unique Username

Unique Endpoint UUID

Unique Enrollment Token

Unique Role Name

---

# 12. Soft Delete Strategy

Critical entities support soft deletion.

```
deleted_at TIMESTAMP
```

Deleted data remains available for auditing.

---

# 13. Audit Strategy

Every critical action generates an audit record.

Examples

- Login
- Logout
- Password Change
- User Creation
- User Deletion
- Endpoint Enrollment
- Remote Command
- Policy Changes
- Configuration Updates

Audit records are immutable.

---

# 14. Data Retention

| Data | Retention |
|-------|-----------|
| Audit Logs | Permanent |
| Command History | Permanent |
| Compliance History | Permanent |
| Alerts | Permanent |
| Performance Metrics | Configurable |
| Inventory Snapshot | Latest + History |

---

# 15. Database Rules

The following rules are mandatory.

- Neon PostgreSQL is the only supported database.
- SQLite is prohibited.
- MySQL is not supported.
- PostgreSQL compatibility must be maintained.
- All schema changes require Alembic migrations.
- Direct production schema modifications are prohibited.
- SSL connections are mandatory.
- Connection pooling must use the Neon Pooler.
- Database credentials must never be committed to Git.

---

# 16. Migration Strategy

Schema changes are managed through Alembic.

Rules

- Every schema change requires a migration.
- Migrations must be reversible.
- Production databases are updated only through migrations.
- Migration history must remain intact.

---

# 17. Future Expansion

The schema supports future modules without redesign.

Examples

- Patch Management
- Software Deployment
- Linux Agent
- macOS Agent
- Multi-Tenant Support
- Asset Lifecycle
- License Management
- Remote Desktop
- AI Assistant

---

# 18. Summary

Sentinel uses Neon PostgreSQL as its enterprise database platform.

The schema is modular, scalable, and designed around business domains rather than monolithic tables.

Business logic remains exclusively within the FastAPI backend while the database is responsible only for reliable, secure, and consistent data storage.

The architecture supports future expansion without requiring major redesign while maintaining compatibility with PostgreSQL standards and modern cloud-native deployments.