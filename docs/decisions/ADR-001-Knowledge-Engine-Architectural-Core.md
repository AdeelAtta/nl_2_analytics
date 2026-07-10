# ADR-001: Knowledge Engine as Architectural Core

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-001 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Most NL2SQL products are built as SQL generation pipelines — knowledge is created per-query and discarded. This architecture fails for enterprise use because (1) adding new capabilities requires restructuring the pipeline, and (2) knowledge about schemas, business meaning, and user preferences is ephemeral. The enterprise data intelligence platform needs persistent, evolving knowledge that all components can access.

## Decision

The Enterprise Knowledge Engine is the single architectural core. All components are consumers or producers of the Knowledge Engine API. No component holds authoritative state.

## Rationale

Knowledge persistence is the fundamental architectural requirement. A pipeline-centric approach treats knowledge as transient (created per-query, discarded after). The Knowledge Engine architecture inverts this: knowledge is persistent, and capabilities are pluggable consumers/producers.

The decision enables:
- **Pluggable capabilities**: New features are new consumers/producers — no pipeline restructuring
- **Knowledge accumulation**: Schema understanding, business meaning, query patterns persist across sessions
- **Horizontal scaling**: Stateless components scale independently; state lives in the Knowledge Engine
- **Deployment flexibility**: Same architecture works in cloud, VPC, on-prem, and air-gapped

## Consequences

### Positive
- New capabilities require adding a new consumer or producer — no pipeline restructuring
- Knowledge accumulates across queries, sessions, and tenants
- Components are independently scalable and deployable
- Five-year product vision (NL2SQL → Multi-DB → Proactive Insights → Autonomous Workflows → Autonomous BI) is a series of new consumers, not rewrites

### Negative
- Higher initial complexity (must build KE API + stores before first SQL query works)
- Additional latency per query (KE API call + store lookups vs direct pipeline)
- KE API is a critical bottleneck that must scale independently

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Pipeline-centric architecture | Brittle — adding capabilities requires pipeline restructuring |
| Monolithic service | Cannot scale components independently |
| Event-driven only | Query path needs synchronous reads — events alone insufficient |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| KE API becomes single point of failure for all query paths | Medium | Critical | KE API HA with horizontal pod autoscaling; circuit breaker in components; cache fallback for known queries |
| KE knowledge grows stale without active learning feedback | Medium | High | Self-learning loop (ADR-010) continuously updates KE; staleness metrics alert when knowledge not refreshed |
| KE API latency degrades as knowledge corpus grows | Medium | Medium | Connection pooling; query result caching (Redis); read replicas for PostgreSQL; KE API request tracing |
| Pipeline-centric mental models drive team to bypass KE API | High | Medium | Enforced by ADR-004 (only internal interface); code review gates; architecture decision recorded |

## Trade-offs

- **Initial complexity vs long-term flexibility**: Building the KE API before any SQL query works adds 4-6 weeks to the initial build. This is accepted because every product capability (NL2SQL, Multi-DB, Proactive Insights, Autonomous Workflows, Autonomous BI) adds as a new KE consumer — avoiding repeated pipeline restructuring that would cost more over 5 years
- **Latency per query vs knowledge persistence**: Every component call includes a KE API network hop (5-15ms added latency). Without KE, queries would be faster but knowledge would be ephemeral — each query starts from zero context
- **Centralized knowledge vs bounded context**: KE concentrates knowledge in one service. Domain-driven design would prefer bounded contexts per capability. However, bounded contexts prevent the cross-domain learning that powers the context layer (e.g., learning query patterns across schemas)

## Related ADRs

- ADR-003: Components Are Stateless Executors (enforced by KE ownership of state)
- ADR-004: KE API Is the Only Internal Interface (KE as sole communication channel)
- ADR-010: Self-Learning Loop Architecture (KE as the target of learning feedback)

## References

- [System-Architecture.md](../System-Architecture.md) §3 (Knowledge Engine), §9 (ADR Index)
- [Architecture-Review.md](../Architecture-Review.md) §10.1
- [KnowledgeEngine-Specification.md](../specifications/KnowledgeEngine-Specification.md)
- [Observability-Specification.md](../specifications/Observability-Specification.md) §5.2 (KE Service Metrics)
