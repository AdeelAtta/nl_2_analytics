# ADR-006: Tenant Isolation at Row/Collection Level

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-006 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform serves 50-5,000+ tenants across Starter, Pro, and Enterprise tiers. Tenant data isolation is a fundamental requirement — one tenant must never access another tenant's schema metadata, query history, or configuration. The architectural question is the isolation granularity.

## Decision

Use shared PostgreSQL tables with row-level tenant IDs + Row-Level Security (RLS), and per-tenant Qdrant collections. Not per-tenant databases or per-tenant infrastructure.

## Rationale

Per-tenant databases at 1,000+ tenants is operationally expensive (1,000 DB instances to manage, 1,000 migrations to run). Per-tenant infrastructure is financially infeasible for mid-market pricing ($50/seat/month). Row-level tenant IDs with RLS provides strong isolation without per-tenant overhead. Qdrant's collection-per-tenant model maps naturally to this approach.

## Consequences

### Positive
- Single PostgreSQL cluster serves all tenants (lower operational cost)
- Schema migrations affect one database, not N databases
- Horizontal scaling via read replicas benefits all tenants
- RLS provides database-enforced isolation (cannot be bypassed by application bugs)
- Per-tenant Qdrant collections enable independent vector index optimization

### Negative
- RLS has performance overhead (PostgreSQL evaluates row-level policy on every access)
- Noisy-neighbor risk (one tenant's heavy query impacts shared PG resources)
- Per-tenant restore is more complex (must filter by tenant_id)
- Qdrant collection count grows linearly with tenants (monitor for 10K+ limits)
- Single PostgreSQL writer bottleneck at scale (mitigated by Citus at >10K tenants)

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Per-tenant databases | Operational cost at 1,000+ tenants; complex schema migrations across N databases |
| Per-tenant K8s namespaces | Resource overhead; namespace management at scale is complex |
| Single-tenant dedicated deployments | Reserved for Enterprise tier only, priced accordingly |
| Shared everything (no tenant isolation) | Security concerns — unacceptable for enterprise customers |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| RLS policy bugs leak data between tenants | Low | Critical | RLS policy unit tests; automated cross-tenant data leak scanning in CI; third-party penetration testing annually |
| Noisy neighbor: one tenant's heavy query degrades all tenants | Medium | High | PostgreSQL statement timeout per query; CPU/memory resource groups; PgBouncer connection pooling with per-tenant limits |
| Qdrant collection count exceeds cluster capacity as tenants grow | Medium | Medium | Monitor tenant-to-collection ratio; implement cold collection archiving; Qdrant cluster horizontal scaling |
| Per-tenant data restore is operationally complex (must filter by tenant_id) | Medium | Medium | Automated restore scripts with tenant_id filter; tested quarterly; documented runbook |

## Trade-offs

- **Shared PG with RLS vs per-tenant databases**: Shared PG minimizes operational overhead (1 cluster, 1 migration pipeline) but forfeits per-tenant resource isolation. Per-tenant databases would isolate resource usage but multiply operational cost at 1,000+ tenants. The trade-off favors shared PG with RLS for V1.0-V2.0; Enterprise tier customers may request dedicated deployments at premium pricing
- **RLS vs application-level filtering**: RLS provides database-enforced isolation that cannot be bypassed by application bugs. Application-level filtering is more flexible (custom per-tenant logic) but creates a security surface area that must be perfect. RLS is chosen because defense-in-depth (RLS + application filtering) is stronger than application-only
- **Per-tenant Qdrant collections vs shared collections with tenant_id filter**: Per-tenant collections provide independent index optimization and natural isolation but increase collection count linearly. Shared collections with tenant_id payload filter reduce collection count but risk index bloat. Per-tenant chosen because Qdrant is optimized for partitioned collections

## Related ADRs

- ADR-002: PostgreSQL + Qdrant as Primary Knowledge Stores (stores implementing isolation)
- ADR-005: Self-Hosted Knowledge Stores Only (self-hosted stores enable tenant isolation without cloud-vendor constraints)
- ADR-015: GPU Vendor Strategy (parallel multi-tenant resource isolation approach)

## References

- [System-Architecture.md](../System-Architecture.md) §7 (Multi-Tenancy), §9 (ADR Index)
- [Architecture-Review.md](../Architecture-Review.md) §10.6
- [Database-Specification.md](../specifications/Database-Specification.md) §5 (Tenant Isolation)
- [Security-Specification.md](../specifications/Security-Specification.md) §3 (Data Isolation)
