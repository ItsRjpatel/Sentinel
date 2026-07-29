# Coding Standards

| Field | Value |
|--------|-------|
| Project | Sentinel |
| Document | Coding Standards |
| Version | 2.0.0 |
| Status | Draft |
| Owner | Development Team |

---

# 1. Purpose

This document defines the coding standards for Sentinel.

All contributors, whether human or AI, must follow these standards to ensure consistency, readability, maintainability, and scalability.

---

# 2. General Principles

- Write clean, readable, and maintainable code.
- Prefer clarity over cleverness.
- Keep functions small and focused.
- One responsibility per class or function.
- Avoid duplicate code (DRY).
- Follow SOLID principles where appropriate.

---

# 3. Python Standards

## Version

Python 3.13+

---

## Naming

Variables

```python
device_name
```

Functions

```python
collect_inventory()
```

Classes

```python
InventoryService
```

Constants

```python
MAX_RETRY_COUNT
```

Private Methods

```python
_validate_token()
```

---

# 4. Type Hints

Every public function should include type hints.

Example

```python
def get_endpoint(endpoint_id: UUID) -> Endpoint:
    ...
```

---

# 5. Docstrings

Public classes and methods should include concise docstrings.

Example

```python
def enroll():
    """Enroll a new endpoint."""
```

---

# 6. Error Handling

- Never ignore exceptions.
- Raise meaningful exceptions.
- Log unexpected errors.
- Never expose internal stack traces to clients.

---

# 7. Logging

Every important operation should log:

- Request ID
- User
- Endpoint
- Action
- Result

Sensitive information must never be logged.

---

# 8. API Standards

- Use REST principles.
- Return consistent JSON.
- Validate input using Pydantic.
- Never trust client input.

---

# 9. Database

- Use SQLAlchemy ORM.
- Never build raw SQL unless necessary.
- Always use Alembic migrations.
- Transactions should be explicit.

---

# 10. Security

- Validate all inputs.
- Hash passwords using Argon2.
- Never hardcode secrets.
- Enforce RBAC.
- Use HTTPS only.

---

# 11. Frontend

- Semantic HTML.
- Bootstrap components where appropriate.
- Vanilla JavaScript only.
- No inline JavaScript.
- Keep CSS modular.

---

# 12. Windows Agent

- Collect data only.
- Never modify database directly.
- Retry transient failures.
- Cache unsent data if offline.

---

# 13. Git Commits

Examples

```
feat(auth): implement JWT login

fix(agent): heartbeat retry bug

docs(api): update endpoint documentation

test(inventory): add hardware tests
```

---

# 14. Pull Request Checklist

- Code compiles
- Tests pass
- Documentation updated
- No unnecessary files
- No secrets committed
- Reviewed

---

# 15. Testing

Every feature should include:

- Unit tests
- Integration tests (where applicable)
- Edge case handling

---

# 16. Code Quality

Required tools:

- Ruff
- Black
- isort
- mypy
- Pytest

---

# 17. Summary

Sentinel prioritizes clean, secure, maintainable, and production-ready code. Every contribution should improve the quality of the project rather than simply adding functionality.
