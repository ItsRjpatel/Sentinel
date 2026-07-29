# Memory
## Project Context
- **Name**: Sentinel
- **Goal**: Build a scalable, agent-based Endpoint Management System.
- **Rules**: Documentation First Development, backend owns business logic, architecture is frozen.

## Technical Decisions
- Python 3.13+, FastAPI, Uvicorn, SQLAlchemy 2.x Async, Alembic.
- PostgreSQL (Neon Database).
- Architecture: Vertical Slice (Feature-First) architecture using Domain-Driven Design principles (`backend/app/modules/`).

## Current State
- **Sprint 1.1 Complete**: Code quality suite verified; global `.venv` and `pyproject.toml` established.
- **Milestone M0.4 Complete**: Foundation Freeze applied. CI pipelines, docker skeletons, and developer config standardizations complete.
- **Milestone M0.5 Complete**: Architecture Migration from Layered to Feature-First. `app/modules/` created, and `app/common/` established.
- **Milestone M1.1 Complete**: Identity & Access Database Models (`User`, `Role`, `Permission`, `RefreshToken`) designed with Pydantic Schemas. Soft delete and UUID mixins successfully added to `app/common/models.py`. Validated via unit tests.
- **Milestone M1.1A Complete**: Authentication Domain Architectural Review completed.
- **Milestone M1.2 Complete**: Authentication Repository Layer (`UserRepository`, `RoleRepository`, `PermissionRepository`, `RefreshTokenRepository`) implemented. Extracted SQLAlchemy exception mapping into `auth.exceptions`.
- **Milestone M1.3 Complete**: Authentication Service Layer (`AuthenticationService`, `pwdlib`, `PyJWT`) implemented to bridge the gap between HTTP APIs and Database logic.
- **Pre-M1.4 Auth Consistency**: Verified `failed_login_attempts`, `last_failed_login`, `locked_until` in user models.
- **Sprint 1 M1.4 DI Layer**: Finished `dependencies.py` wiring `AuthenticationService`.
- **Sprint 1 M1.5A/B API**: Finished Authentication API design and routing implementation.
- **Milestone M1.5.1 Complete**: Validation Review. Successfully validated 100% of endpoints against API specification. Test suite verified passing.
- **Sprint 1 M1.6 Infrastructure**: Completed Token and Security implementations.
- **Milestone M1.6 Complete**: JWT Authentication Infrastructure. Created centralized security exceptions, robust token decoding/verification, and reusable `get_current_user` and `require_permission` authorization dependencies.
- **Sprint 1 M1.7 Bootstrap**: Created standalone initialization scripts for idempotent database seeding.
- **Milestone M1.7 Complete**: Bootstrap Admin & System Initialization. Created idempotent scripts to inject initial roles, permissions, and the super administrator, avoiding application startup pollution.
- **M1.8A Migration Recovery**: Restored initial schema migration to `99fe757562ae_initial_schema.py` and validated on Neon PostgreSQL.
- **Sprint 1 M1.8 Integration Testing**: Pending restart.

## Next Steps
- Wait for user instruction to begin Milestone M1.8 (Integration Testing).