# EP-009: NL2SQL Generation

Epic ID: **EP-009** | Priority: **P0** | Dependencies: **EP-008** | Complexity: **XL** | Agent: **Query Pipeline Agent**

---

Implement the NL2SQL Generation subsystem — the core SQL generation pipeline with multi-candidate generation, tiered model routing, and candidate selection.

## Goals
- SQL generation via 3 model tiers (SQLCoder-7b-2, Qwen2.5-72B, DeepSeek-V3)
- Multi-candidate generation (top-K candidates per model)
- Candidate selection (best SQL from candidates)
- Tiered routing fallback (simple -> medium -> complex -> GPT-4o fallback)
- LangGraph agent orchestration
- Cost tracking per query

## Out of Scope
- Validation and repair (EP-010 handles this)
- Guardrails (EP-010)
- Query execution (EP-011)

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-067 | Implement LangGraph agent orchestration framework | P0 | EP-008 | XL |
| TASK-068 | Build SQLCoder-7b-2 inference wrapper (simple tier) | P0 | TASK-067 | M |
| TASK-069 | Build Qwen2.5-72B inference wrapper (medium tier) | P0 | TASK-067 | M |
| TASK-070 | Build DeepSeek-V3 inference wrapper (complex tier) | P1 | TASK-067 | M |
| TASK-071 | Implement GPT-4o fallback integration | P1 | TASK-067 | M |
| TASK-072 | Implement multi-candidate generator | P0 | TASK-068 | L |
| TASK-073 | Implement candidate selector | P0 | TASK-072 | L |
| TASK-074 | Implement Reflection Agent (self-critique) | P0 | TASK-072 | L |
| TASK-075 | Implement Repair Agent (fix common errors) | P0 | TASK-074 | L |
| TASK-076 | Build inference abstraction layer | P0 | TASK-067 | L |
| TASK-077 | Implement cost tracking and budget enforcement | P0 | TASK-067 | M |
| TASK-078 | Write unit and integration tests | P0 | TASK-072 | XL |

## Acceptance Criteria
- E2E SQL generation for simple queries < 2s, complex < 8s
- Execution accuracy > 60% on enterprise benchmark
- Cost tracking within budget ($0.006/query weighted average)
- Reflection catches > 80% of incorrect SQL
- Repair fixes > 60% of caught errors

## Definition of Done
- Full generation pipeline end-to-end tested
- Accuracy benchmarks against Spider 2.0 enterprise subset
- Cost benchmarks within budget
