# ADR-004: Knowledge Engine API Is the Only Internal Interface

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-004 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

With multiple components that read and write knowledge, there are many possible communication patterns. Components could talk directly to each other, read knowledge stores directly, or communicate through an event bus. The choice affects coupling, testability, deployability, and evolvability.

## Decision

No component talks to another component directly. No component reads a knowledge store directly. All communication goes through the Knowledge Engine API (port 8200).

## Rationale

Loose coupling is the primary benefit: changing a store (e.g., swapping PostgreSQL for CockroachDB) requires zero component changes — only the KE API changes. Testing improves: each component can be tested in isolation with a KE API mock. Deployment flexibility increases: components can be deployed independently and in any order.

This decision also makes ADR-003 (stateless components) enforceable — no component can hold state if it cannot directly access stores.

## Consequences

### Positive
- Changing a store requires zero component changes — only KE API changes
- Each component testable in isolation with KE API mock
- Components deploy independently, in any order
- Enforces stateless discipline — no direct store access means no component-level state

### Negative
- Additional latency: every component call goes through KE API network hop vs direct store access
- KE API becomes a critical bottleneck — must scale independently with its own horizontal pod autoscaling
- All store schema changes must be reflected in KE API first

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Direct store access | Tight coupling — changing a store breaks all components |
| Event bus only | Query path needs synchronous request-response — events alone insufficient |
| Inter-component HTTP | Tight coupling — components must know each other's addresses |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| KE API becomes performance bottleneck as request volume grows | High | Critical | Horizontal autoscaling per KE API endpoint; connection pooling; Redis cache for reads; async writes via message queue |
| Component team bypasses KE API for "emergency" direct store access | Medium | High | Git hook preventing direct store credentials in component repos; code review enforcement; architecture compliance CI check |
| KE API contract changes break multiple components simultaneously | Medium | Medium | Versioned API endpoints; backward-compatible additions; deprecation headers with 2-release grace period |
| Latency overhead from double network hop (component → KE API → store) | Medium | Medium | Keep-alive connections; response streaming for large payloads; co-location in same K8s cluster |

## Trade-offs

- **Loose coupling vs performance**: Every component → KE API → store trip adds ~10-15ms vs direct component → store access. A typical query involves 5-15 KE API calls, totaling 50-200ms overhead per query. This is acceptable (end-to-end latency budget is P50 ~2.8s, P95 ~6.1s, P99 ~8.1s) and the loose coupling benefit is significant
- **KE API as monolith vs split into domain services**: A single KE API is simpler to deploy and version but creates a large surface area. If it grows beyond maintainable scope, it can be split into domain-specific services behind the same interface contract. This is a future optimization, not a current concern
- **Synchronous vs async communication**: Query paths require synchronous request-response (component waits for KE API). Background operations (learning loop, enrichment) can use async messaging. The ADR covers both: KE API handles sync reads/writes; KE publishes events for async consumers

## Related ADRs

- ADR-001: Knowledge Engine as Architectural Core (KE API is the interface to the core)
- ADR-003: Components Are Stateless Executors (enforced by KE API as only state access)
- ADR-010: Self-Learning Loop Architecture (async feedback path via KE API)

## References

- [System-Architecture.md](../System-Architecture.md) §6 (API Design), §9 (ADR Index)
- [Architecture-Review.md](../Architecture-Review.md) §10.4
- [API-Design.md](../API-Design.md) §3 (KE API Specification)
- [Observability-Specification.md](../specifications/Observability-Specification.md) §5.2 (KE API Metrics)
