# TASK-102: Scaffold Public API FastAPI Service

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-102 |
| **Epic** | EP-013 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | EP-001 |
| **Agent Owner** | API Agent |
| **Status** | backlog |

---

## Description

Scaffold the public API FastAPI service (port 8100) with OpenAPI spec generation, middleware setup, and route stubs.

## Inputs

- API-Design.md (full API contract)
- EP-013 epic definition

## Implementation

Create `/backend/api/main.py`:

```python
# FastAPI app on port 8100
# OpenAPI spec: /docs, /openapi.json
# Middleware stack:
#   1. CORS (allow frontend origin)
#   2. Request ID (generate unique ID per request)
#   3. Logging (log method, path, status, duration)
#   4. Rate limiting
#   5. Auth (JWT verification)
#
# Routers:
#   /v1/auth     - auth.py
#   /v1/query    - query.py
#   /v1/schemas  - schemas.py
#   /v1/history  - history.py
#   /v1/feedback - feedback.py
#   /v1/admin    - admin.py
#
# Root /health endpoint
```

Create `/backend/api/config.py` with settings for:
- JWT secret, algorithm, expiry
- Rate limit (requests/min per tenant)
- Allowed origins (CORS)
- KE API URL (internal)
- Service token (for KE API auth)

## Outputs

- `/backend/api/main.py`
- `/backend/api/config.py`
- `/backend/api/dependencies.py`
- `/backend/api/middleware/` (stubs)
- `/backend/api/routes/` (stubs for all route modules)

## Acceptance Criteria

- [ ] App starts on port 8100
- [ ] /health returns 200
- [ ] /docs renders OpenAPI spec
- [ ] CORS headers returned correctly
- [ ] Request ID added to every response
- [ ] Route stubs return 501 Not Implemented

## Definition of Done

- App starts in dev mode
- Health check passes
- OpenAPI spec browsable
- Task status updated to `done`
