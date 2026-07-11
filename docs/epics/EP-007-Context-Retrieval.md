# EP-007: Context Retrieval

Epic ID: **EP-007** | Priority: **P0** | Dependencies: **EP-005** | Complexity: **Medium** | Agent: **Query Pipeline Agent**

---

Implement the Context Retrieval Agent — the subsystem that retrieves relevant schema context, graph paths, and historical patterns from the Knowledge Engine to inform SQL generation.

## Goals
- Hybrid search (vector + keyword + graph) given a user query
- Context ranking and deduplication
- Context size management (stay within LLM context window)
- Multi-source fusion: schema, relationships, historical queries, business terms
- Caching for repeated queries

## Out of Scope
- Schema population (EP-006)
- Intent classification (EP-008)
- SQL generation (EP-009)

## Tasks

| ID | Name | P | Deps | Est | Status |
|----|------|---|---|------|--------|
| TASK-042 | Build QueryService (hybrid context search + DDL enrichment) | P0 | EP-005, EP-003 | XL | ✅ done |
| TASK-043 | Build DDLRenderer + Discover endpoint | P0 | EP-005 | L | ✅ done |

### Original plan tasks (superseded by TASK-042/043)

| ID | Name | P | Deps | Est | Status |
|----|------|---|---|------|--------|
| TASK-056 | Implement query embedding service | P0 | EP-003 | M | ⏳ merged into TASK-042 |
| TASK-057 | Build hybrid retriever | P0 | TASK-056, EP-005 | XL | ⏳ merged into TASK-042 |
| TASK-058 | Implement context ranking and dedup | P0 | TASK-057 | L | ⏳ not started |
| TASK-059 | Build context window trimmer | P0 | TASK-058 | M | ⏳ not started |
| TASK-060 | Implement query result cache | P1 | TASK-057 | M | ⏳ not started |
| TASK-061 | Write unit and integration tests | P0 | TASK-057 | L | ⏳ merged into TASK-042 |

## Status: 🏗️ Partially Complete — QueryService + DDLRenderer + 4 query endpoints built (25 tests). Remaining: ranking/dedup, window trimmer, cache.

## What was built
- `backend/ke/services/query.py` — QueryService (hybrid vector search + DDL enrichment), DDLRenderer (CREATE TABLE rendering with type mapping, PKs, FKs, constraints)
- `backend/ke/api/routes/query.py` — 4 endpoints: POST /v1/ke/query/context, GET /v1/ke/query/context/table/{table_id}, POST /v1/ke/query/render-ddl, GET /v1/ke/query/discover
- 21 service tests + 4 API tests (25 total)

## Acceptance Criteria
- Retrieves relevant schema context for 90%+ of test queries
- Context window fits within 8K tokens (configurable)
- Deduplication removes >50% redundant schema entries
- Cache hit returns in < 5ms
- Integration tests pass with real KE stores

## Definition of Done
- E2E retrieval tested with sample enterprise database
- Context quality evaluated (retrieval precision > 0.8)
