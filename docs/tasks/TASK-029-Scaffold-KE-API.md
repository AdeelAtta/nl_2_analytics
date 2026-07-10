# TASK-029: Scaffold KE API FastAPI Service

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-029 |
| **Epic** | EP-005 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | TASK-001 |
| **Agent Owner** | Knowledge Engine Agent |
| **Status** | backlog |

---

## Description

Scaffold the Knowledge Engine API FastAPI service. Create the application entry point, configuration, and basic middleware structure. This is the foundation for all KE API routes.

## Inputs

- Implementation-Plan.md (API structure)
- Component-Design.md §5 (KE API section)

## Implementation

1. Create `/backend/ke/api/main.py`:
   - FastAPI app with title "Knowledge Engine API"
   - Port 8200 (internal only)
   - OpenAPI disabled for internal service (or restricted)

2. Create `/backend/ke/api/config.py`:
   - Database URLs (PG, Qdrant)
   - Service token config
   - Store settings

3. Create `/backend/ke/api/dependencies.py`:
   - KE client dependency injection
   - Tenant context dependency
   - Auth dependency

4. Create `/backend/ke/api/middleware/__init__.py`:
   - Tenant middleware (extract tenant_id from header)
   - Auth middleware (validate service token)
   - Request ID middleware

## Outputs

- `/backend/ke/api/main.py`
- `/backend/ke/api/config.py`
- `/backend/ke/api/dependencies.py`
- `/backend/ke/api/middleware/__init__.py`

## Acceptance Criteria

- [ ] FastAPI app starts on port 8200
- [ ] Health check endpoint returns 200
- [ ] Tenant middleware extracts tenant_id from header
- [ ] Auth middleware rejects requests without valid token
- [ ] Config loads from environment with sensible defaults

## Test Requirements

- Integration test: app starts and responds to health check
- Unit test: middleware rejects invalid tokens
- Unit test: middleware extracts correct tenant_id

## Definition of Done

- App starts in development mode
- Health check passes
- Middleware tests pass
- Task status updated to `done`
