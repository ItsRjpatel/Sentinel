# SECURITY DOCUMENTATION

## 1. Agent Identity and DPAPI
The agent persists its configuration and JWTs in `identity.json`. This file is encrypted at rest using the Windows Data Protection API (DPAPI) tied to the machine context (`CRYPTPROTECT_LOCAL_MACHINE`). This prevents credential theft if the file is copied to another machine.

## 2. API Security
- **HTTPS**: All communication between the agent, frontend, and backend occurs over TLS/SSL.
- **JWT**: Admin and Agent endpoints require valid JSON Web Tokens. Admin tokens use standard Bearer auth, while agent tokens identify the specific machine UUID.

## 3. Command Security limitations
The current command orchestration allows predefined scripts or arbitrary strings depending on configuration. Security is dependent on the backend trusting the authenticated administrator. Execution runs under the privileges of the Windows Service (typically LocalSystem).
