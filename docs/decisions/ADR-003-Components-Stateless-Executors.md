# ADR-003: Components Are Stateless Executors

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-003 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Components in the data intelligence platform need to be scalable, deployable across multiple modes (cloud/VPC/on-prem/air-gapped), and individually maintainable. The architectural question is whether components should hold state locally or delegate all state management to the Knowledge Engine.

## Decision

All components are stateless executors. All state lives in the Knowledge Engine. Components can be killed and restarted without data loss.

## Rationale

Stateless services can be scaled horizontally (add pods), rolled with zero downtime (Kuberentes rolling update), and deployed in any mode without state migration. Debugging is simpler — reproduce issues by replaying inputs, with no hidden state to reconstruct.

## Consequences

### Positive
- Horizontal scaling is trivial — add pods, no session affinity needed
- Zero-downtime deployments with K8s rolling updates
- Same component image works in all 5 deployment modes
- Debugging is reproducible — replay inputs, no hidden state
- Components can be killed and restarted without data loss

### Negative
- Every request includes a KE API network hop (additional latency per call)
- Some operations that could be fast with local state (e.g., schema cache) require a network call
- KE API becomes the single source of truth — must be highly available

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Stateful services | Complicates scaling; requires sticky sessions; state migration between deployment modes is complex |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Component relies on local cache for performance but ADR forbids local state | Medium | Medium | Allow ephemeral caches with TTL < 60s and explicit lifecycle bound to pod lifetime — no persistent local state |
| Network hop to KE API becomes latency bottleneck | Medium | High | Connection pooling; keep-alive connections; co-locate KE API in same AZ; Redis cache for hot data paths |
| Component design implicitly assumes stateful behavior (e.g., in-memory counters) | Medium | Low | Code review checklist for stateless compliance; linting rule against instance variables; statelessness in testing manifesto |

## Trade-offs

- **Stateless simplicity vs local cache performance**: Stateless components are trivially scalable but every operation requires a KE API network round-trip. Read-heavy paths (schema lookup, table metadata) that could be ~1ms locally become ~10ms with KE API hop. The trade-off favors scalability over peak single-instance performance — acceptable because horizontal scaling compensates
- **Pure statelessness vs pragmatic ephemeral state**: Pure statelessness means no local caching at all. Pragmatic statelessness allows ephemeral caches (TTL < 60s, lost on pod restart). The pragmatic approach is chosen: components may cache hot KE reads for < 60s but must tolerate cache loss at any time
- **Debugging simplicity vs observability cost**: Stateless debugging is simpler (replay inputs = reproduce) but requires comprehensive tracing to correlate requests across components. Acceptable because OpenTelemetry tracing is already a platform requirement (ADR-016)

## Related ADRs

- ADR-001: Knowledge Engine as Architectural Core (KE owns state; components don't)
- ADR-004: KE API Is the Only Internal Interface (enforces stateless by preventing direct store access)

## References

- [System-Architecture.md](../System-Architecture.md) §5 (Component Design), §9 (ADR Index)
- [Architecture-Review.md](../Architecture-Review.md) §10.3
- [Component-Design.md](../Component-Design.md) §2 (Design Principles)
- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §3 (Immutable Artifacts)
