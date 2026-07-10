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

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-056 | Implement query embedding service | P0 | EP-003 | M |
| TASK-057 | Build hybrid retriever (vector + keyword + graph) | P0 | TASK-056, EP-005 | XL |
| TASK-058 | Implement context ranking and deduplication | P0 | TASK-057 | L |
| TASK-059 | Build context window trimmer | P0 | TASK-058 | M |
| TASK-060 | Implement query result cache | P1 | TASK-057 | M |
| TASK-061 | Write unit and integration tests | P0 | TASK-057 | L |

## Acceptance Criteria
- Retrieves relevant schema context for 90%+ of test queries
- Context window fits within 8K tokens (configurable)
- Deduplication removes >50% redundant schema entries
- Cache hit returns in < 5ms
- Integration tests pass with real KE stores

## Definition of Done
- E2E retrieval tested with sample enterprise database
- Context quality evaluated (retrieval precision > 0.8)
