# EP-008: Intent Analysis & Query Planning

Epic ID: **EP-008** | Priority: **P0** | Dependencies: **EP-007** | Complexity: **Large** | Agent: **Query Pipeline Agent**

---

Implement the Intent Analysis and Query Planning agents — the first two agents in the 10-agent NL2SQL pipeline that classify user intent and plan the SQL generation approach.

## Goals
- Intent classification (list, aggregate, join, filter, nested, unknown)
- Domain identification (which business domain does query target)
- Query decomposition (sub-queries for multi-step questions)
- Query plan generation (which tables, which join paths, which filters)
- Plan validation (is the query plan feasible given available schema)
- Router decision (which model tier to use)

## Out of Scope
- SQL generation (EP-009)
- Final validation (EP-010 has dedicated validation)

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-062 | Implement Intent Agent (classify + route) | P0 | EP-007 | L |
| TASK-063 | Build query plan generation logic | P0 | TASK-062 | XL |
| TASK-064 | Implement plan validation and feasibility check | P0 | TASK-063 | L |
| TASK-065 | Implement model router (tier selection logic) | P0 | TASK-062 | M |
| TASK-066 | Write unit and integration tests | P0 | TASK-062 | L |

## Acceptance Criteria
- Intent classification accuracy > 95% on test set
- Query plan covers all necessary schema elements for > 85% of queries
- Plan validation catches infeasible plans with > 90% precision
- Model router selects correct tier for 90%+ of queries
- Processing time: Intent + Planning < 500ms P95

## Definition of Done
- Intent + Planning pipeline end-to-end tested
- Accuracy benchmarks met
