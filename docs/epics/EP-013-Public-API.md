# EP-013: Public API Layer

Epic ID: **EP-013** | Priority: **P0** | Dependencies: **EP-005, EP-011** | Complexity: **Large** | Agent: **API Agent**

---

Implement the Public REST API gateway (port 8100) that exposes the platform's capabilities to external consumers: frontend, CLI, SDK, and integrations. Follows the API contract defined in docs/API-Design.md.

## Goals
- FastAPI service on port 8100 (public facing)
- Authentication (JWT-based, API key support)
- Rate limiting per tenant/user
- Query endpoint (full NL2SQL pipeline trigger)
- Schema exploration endpoints
- History and feedback endpoints
- Admin endpoints
- OpenAPI spec
- Request/response logging
- CORS configuration

## Out of Scope
- Knowledge Engine API (EP-005 handles internal API)
- Frontend UI (EP-014)
- Query pipeline logic

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-102 | Scaffold Public API FastAPI service | P0 | EP-001 | M |
| TASK-103 | Implement JWT auth middleware | P0 | TASK-102 | L |
| TASK-104 | Implement API key auth | P1 | TASK-103 | M |
| TASK-105 | Implement rate limiting middleware | P0 | TASK-102 | M |
| TASK-106 | Implement CORS configuration | P0 | TASK-102 | S |
| TASK-107 | Implement query endpoint | P0 | TASK-102, EP-011 | L |
| TASK-108 | Implement schema exploration endpoints | P0 | TASK-102, EP-005 | L |
| TASK-109 | Implement history endpoints | P1 | TASK-102 | M |
| TASK-110 | Implement feedback endpoints | P0 | TASK-102 | M |
| TASK-111 | Implement admin endpoints | P1 | TASK-102 | L |
| TASK-112 | Add request/response logging middleware | P0 | TASK-102 | M |
| TASK-113 | Write unit and integration tests | P0 | TASK-107 | XL |

## Acceptance Criteria
- All endpoints from API-Design.md implemented
- JWT auth rejects invalid/expired tokens
- API key auth works as alternative
- Rate limiting correctly throttles at configured limits
- Query endpoint triggers full NL2SQL pipeline and returns results
- OpenAPI spec auto-generated and accessible at /docs
- CORS configured for frontend origin
- All error responses follow standard format

## Definition of Done
- All public API endpoints implemented and tested
- Auth tests (JWT + API key) pass
- Rate limiting stress-tested
- E2E test: query -> response
