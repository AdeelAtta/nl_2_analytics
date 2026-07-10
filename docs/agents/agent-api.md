# Agent: API

| Metadata | Value |
|----------|-------|
| **Agent ID** | AGENT-API |
| **Owns Epics** | EP-013 |
| **Workspace** | `/backend/api/` |
| **Reads** | `/docs/API-Design.md`, `/docs/epics/EP-013` |

---

## Responsibilities

1. Implement public REST API (FastAPI, port 8100)
2. Implement JWT + API key authentication middleware
3. Implement rate limiting middleware
4. Implement CORS configuration
5. Wire query endpoint to query pipeline
6. Implement schema exploration endpoints
7. Implement history and feedback endpoints
8. Implement admin endpoints
9. Add request/response logging
10. Generate OpenAPI spec

## Workspace Boundaries

```
/backend/api/
  __init__.py
  main.py                   -> FastAPI app
  /routes/
    query.py                -> Query endpoint
    schemas.py              -> Schema exploration
    history.py              -> Query history
    feedback.py             -> Feedback submission
    admin.py                -> Admin endpoints
    auth.py                 -> Auth endpoints
  /middleware/
    auth.py                 -> JWT + API key auth
    rate_limit.py           -> Rate limiting
    logging.py              -> Request/response logging
    cors.py                 -> CORS configuration
  dependencies.py
  config.py
```

## DO NOT Touch

- `/backend/ke/`
- `/backend/schema-intelligence/`
- `/backend/query-pipeline/`
- `/frontend/`
- `/infra/`

## Prompts

### Public API Setup Prompt
```
Implement the Public API gateway.

Create main.py with:
- FastAPI app with OpenAPI config
- Include all routers from /routes/
- Add middleware: auth, rate_limit, logging, cors
- Health check endpoint at /health

Create routes/query.py:
- POST /v1/query -> triggers NL2SQL pipeline
- Input: { "query": "string", "database_id": "string", "options": {} }
- Output: { "id": "string", "sql": "string", "results": [...], "execution_time_ms": int }
- Wire to Query Pipeline service

Reference API-Design.md for full endpoint specifications.
```

## Definition of Done
- All routes from API-Design.md implemented
- Auth tests pass (JWT + API key)
- Rate limiting stress-tested
- OpenAPI spec generated at /docs
- All task status files updated
