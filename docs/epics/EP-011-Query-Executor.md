# EP-011: Query Executor

Epic ID: **EP-011** | Priority: **P0** | Dependencies: **EP-010** | Complexity: **Medium** | Agent: **Query Pipeline Agent**

---

Implement the Query Executor — the component that safely executes validated SQL against the target database, manages connections, handles errors gracefully, and formats results.

## Goals
- SQL execution against target database via SQLAlchemy
- Connection pooling per database
- Result set formatting (rows to structured JSON)
- Error handling (timeout, syntax, connection, permission errors)
- Execution timeout enforcement
- Result pagination for large result sets
- Dry-run mode (EXPLAIN only, no execution)

## Out of Scope
- SQL generation (EP-009)
- Guardrails (EP-010)
- Result caching (EP-007 handles query-level caching)

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-088 | Implement connection pool manager | P0 | EP-010 | M |
| TASK-089 | Implement SQL executor with timeout | P0 | TASK-088 | L |
| TASK-090 | Implement result formatter (rows to JSON) | P0 | TASK-089 | M |
| TASK-091 | Implement error handler and classification | P0 | TASK-089 | M |
| TASK-092 | Implement dry-run mode | P1 | TASK-089 | S |
| TASK-093 | Implement result pagination | P1 | TASK-089 | M |
| TASK-094 | Write unit and integration tests | P0 | TASK-089 | L |

## Acceptance Criteria
- Executes SQL and returns formatted results in < 100ms overhead
- Connection pooling reuses connections correctly
- Timeout enforcement kills queries exceeding limit
- Error classification maps DB errors to standard codes
- Dry-run returns EXPLAIN output without executing
- Pagination works for result sets > 1000 rows

## Definition of Done
- E2E execution tested against PostgreSQL
- Connection pool stress-tested (100 concurrent queries)
- All error paths tested
