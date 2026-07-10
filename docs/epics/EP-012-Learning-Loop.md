# EP-012: Learning Loop & Feedback

Epic ID: **EP-012** | Priority: **P1** | Dependencies: **EP-005, EP-011** | Complexity: **Large** | Agent: **Knowledge Engine Agent**

---

Implement the Learning Loop — the asynchronous feedback processing pipeline that transforms user feedback and query logs into Knowledge Engine improvements. This is the closed-loop self-learning mechanism.

## Goals
- Feedback collection via KE Feedback Store
- Feedback validation (reject spam, check consistency)
- Q&A pair generation from successful queries
- Schema enrichment (improve descriptions based on user corrections)
- Pattern mining (detect frequent table joins, common query patterns)
- Regular batch processing (5-minute cycle)
- Online learning rejection (batch only to prevent quality degradation)

## Out of Scope
- Model fine-tuning (Phase 3)
- Real-time feedback incorporation
- A/B testing framework

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-095 | Implement feedback collector | P0 | EP-005 | M |
| TASK-096 | Build feedback validator and deduplicator | P0 | TASK-095 | L |
| TASK-097 | Implement Q&A pair builder | P1 | TASK-095 | L |
| TASK-098 | Implement schema enricher | P1 | TASK-095 | L |
| TASK-099 | Implement pattern miner | P1 | TASK-095 | L |
| TASK-100 | Build batch scheduler (5-min cycle) | P0 | TASK-095 | M |
| TASK-101 | Write unit and integration tests | P0 | TASK-095 | L |

## Acceptance Criteria
- Feedback collected, validated, deduplicated within 5-minute batch cycle
- Q&A pairs generated from successful queries with > 90% valid pairs
- Schema enricher improves column descriptions based on user corrections
- Pattern miner detects top-10 most common join patterns
- Batch processing handles 10K feedback items per cycle
- No feedback incorporated without passing all quality checks

## Definition of Done
- E2E learning loop tested: feedback submission -> batch processing -> KE update
- Quality metrics: < 1% incorporation of bad feedback
- Performance: batch processes 10K items in < 30s
