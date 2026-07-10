# ADR-010: Self-Learning Loop Architecture

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-010 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform must improve over time by learning from user feedback, query patterns, and schema changes. The learning loop design affects accuracy improvement rate, risk of bad feedback degrading the system, and the latency between user correction and system improvement.

## Decision

Asynchronous batch learning loop. Feedback collected per-query, validated in batch, written to Knowledge Engine. No online learning.

## Rationale

Online learning (update model per feedback) is high-risk — bad feedback immediately degrades accuracy. It also adds latency to the query path if feedback writes are synchronous. Batch learning allows validation, deduplication, and quality checks before knowledge is updated. The 5-minute batch cycle provides a reasonable feedback-to-improvement latency.

## Consequences

### Positive
- Bad feedback is caught and filtered before it affects the system
- Feedback quality checks (consistency, deduplication, confidence scoring) run before any knowledge update
- No impact on query path latency (feedback is collected asynchronously)
- Batch processing enables aggregation — patterns are learned, not individual corrections

### Negative
- Feedback-to-improvement latency of ~5-15 minutes end-to-end
- User does not see immediate improvement from their correction
- Batch infrastructure adds operational complexity (scheduler, worker, dead-letter queue)
- System may produce the same error multiple times within a batch window

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Online learning (per-feedback update) | Bad feedback immediately degrades accuracy; blocking writes increase query latency |
| Periodic full retrain | Slow improvement cycle (days/weeks); stale model between retrains |
| No learning loop | System never improves — competitive disadvantage |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Bad feedback passes validation and degrades knowledge quality | Medium | High | Multi-stage validation (consistency check → deduplication → confidence scoring); human-in-the-loop for low-confidence feedback |
| Feedback volume exceeds batch processing capacity | Medium | Medium | Auto-scaling worker pool; dead-letter queue for failed items; feedback sampling at extreme volume |
| Learning loop amplifies systematic biases (e.g., always suggesting same table) | Medium | Medium | Diversity metrics on learning output; diversity-aware sampling in feedback aggregation |
| Batch cycle latency too slow for user expectations of improvement | Medium | Medium | User-visible "learning" indicator; expectation setting in UX; consider incremental update for high-confidence feedback |

## Trade-offs

- **Batch learning vs online learning**: Batch learning trades feedback-to-improvement latency (5-15 minutes) for safety (validation before knowledge update). Online learning would show immediate improvement from corrections but risks bad feedback immediately degrading accuracy. Batch chosen because safety is prioritized over speed for enterprise knowledge
- **5-minute batch window vs hourly/daily**: 5 minutes provides near-real-time improvement without the infrastructure cost of streaming. Hourly would reduce infra cost but feel unresponsive. Daily would be unacceptable for user experience. 5 minutes is the pragmatic balance
- **Feedback quality scoring vs accepting all feedback**: Quality scoring (consistency, confidence, deduplication) filters ~15-30% of feedback as low-quality. Accepting all feedback would accelerate learning but risk knowledge degradation. Scoring adds batch complexity but is essential for knowledge quality

## Related ADRs

- ADR-001: Knowledge Engine as Architectural Core (learning loop writes to KE)
- ADR-003: Components Are Stateless Executors (learning agent is stateless executor)
- ADR-004: KE API Is the Only Internal Interface (learning loop writes through KE API)
- ADR-008: Tiered Model Routing (learning loop improves routing decisions over time)

## References

- [Architecture-Review.md](../Architecture-Review.md) §10.10
- [KnowledgeEngine-Specification.md](../specifications/KnowledgeEngine-Specification.md) §5 (Learning & Feedback)
- [AI-Agent-Specification.md](../specifications/AI-Agent-Specification.md) §7 (Learning Agent)
- [Observability-Specification.md](../specifications/Observability-Specification.md) §5.2 (Learning Loop Metrics)
