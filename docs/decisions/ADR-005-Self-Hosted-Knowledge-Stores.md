# ADR-005: Self-Hosted Knowledge Stores Only

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-005 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform must support 5 deployment modes: multi-tenant cloud SaaS, dedicated cloud, customer VPC, on-premises Kubernetes, and air-gapped. Knowledge stores (PostgreSQL, Qdrant, Redis) are the most stateful and deployment-sensitive components. Cloud-managed store services simplify operations but create deployment-mode lock-in.

## Decision

All knowledge stores (PostgreSQL, Qdrant, Redis) are self-hosted. No cloud-managed store services are used for core Knowledge Engine operation.

## Rationale

Self-hosted stores provide the same architecture across all 5 deployment modes. No external API dependency for core Knowledge Engine operation. Consistent performance characteristics across deployment modes — what works in cloud works identically in air-gapped environments.

## Consequences

### Positive
- Same architecture works in cloud, VPC, on-prem, and air-gapped
- No external API dependency for core KE operation
- Consistent performance characteristics across all deployment modes
- No cloud vendor lock-in at the storage layer

### Negative
- Higher operational overhead — must manage PostgreSQL HA, Qdrant cluster, Redis replication
- Cannot leverage cloud-managed auto-scaling (Aurora, Cloud SQL, ElastiCache)
- Requires in-house operational expertise for PostgreSQL and Qdrant
- Backup/recovery procedures must be self-managed

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Cloud-managed PostgreSQL (RDS/Cloud SQL) | Violates deployment-agnostic principle; on-prem/air-gapped impossible |
| Cloud-managed Qdrant (Qdrant Cloud) | Same as above |
| Cloud-managed Redis (ElastiCache) | Same as above |
| Pinecone | Cloud-only, closed-source, violates deployment-agnostic principle |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Self-hosted PostgreSQL HA fails during AZ outage | Medium | Critical | Streaming replication across AZs; Patroni for automated failover; regular failover drills |
| Self-hosted Qdrant cluster management exceeds team operational capacity | Medium | High | Managed Qdrant Cloud considered as operational fallback; dedicated ops runbook; monitoring for cluster health |
| Storage backup/restore procedures fail during actual disaster | Low | Critical | Automated daily backups with verified restore (restore test every 7 days); backup stored in separate region |
| In-house operational expertise insufficient for PostgreSQL performance tuning | Medium | Medium | Enable PostgreSQL expert consulting retainer; invest in team training; use managed PG for dev/staging |

## Trade-offs

- **Self-hosted vs cloud-managed stores**: Cloud-managed (RDS, ElastiCache, Qdrant Cloud) eliminates operational overhead but creates deployment-mode lock-in. Self-hosted is chosen because deployment-agnosticism (5 modes from SaaS to air-gapped) is a core architectural principle. The operational cost is accepted as the price of flexibility
- **One PostgreSQL cluster vs per-tenant clusters**: A single cluster simplifies operations (1 DB to manage, 1 set of migrations) at the cost of noisy-neighbor risk. Per-tenant clusters isolate tenants but explode operational complexity at 1,000+ tenants. The trade-off favors single-cluster for V1.0, with Citus or per-tenant clusters evaluated at >10K tenants
- **Qdrant cluster vs single-node**: Single Qdrant node is sufficient for MVP (<100 tenants, <1M vectors). Cluster mode adds replication and sharding complexity. Start with single-node, add cluster at 500+ tenants or when HA requirement kicks in

## Related ADRs

- ADR-002: PostgreSQL + Qdrant as Primary Knowledge Stores (the stores being self-hosted)
- ADR-006: Tenant Isolation at Row/Collection Level (works with self-hosted stores)
- ADR-015: GPU Vendor Strategy (parallel self-hosting philosophy)

## References

- [System-Architecture.md](../System-Architecture.md) §4 (Data Stores), §9 (ADR Index)
- [Architecture-Review.md](../Architecture-Review.md) §10.5
- [Deployment-Architecture.md](../Deployment-Architecture.md) §5 (Storage Architecture)
- [Infrastructure-Specification.md](../specifications/Infrastructure-Specification.md) §3 (Storage Infrastructure)
- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §10 (DB Migration Operations), §15 (Disaster Recovery)
