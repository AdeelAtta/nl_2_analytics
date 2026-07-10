# ADR-008: Tiered Model Routing (Not Single Model)

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-008 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Each NL2SQL query requires an LLM call for SQL generation. Using the most capable model (GPT-4o) for every query is cost-prohibitive. However, a single cheaper model may not handle complex enterprise queries. The choice of model routing strategy directly affects the cost structure and accuracy.

## Decision

Route queries to cheap/medium/expensive models based on complexity tier. SQLCoder-7b (simple) / Qwen2.5-72B (medium) / DeepSeek-V3 (complex) / GPT-4o (fallback).

| Tier | Model | Cost/Query | Expected % of Queries |
|------|-------|-----------|----------------------|
| Simple | SQLCoder-7b-2 | $0.0003 | 65% |
| Medium | Qwen2.5-72B | $0.002 | 20% |
| Complex | DeepSeek-V3 | $0.01 | 10% |
| Fallback | GPT-4o | $0.02 | 5% |

## Rationale

65% of enterprise queries are simple (1-2 tables, basic WHERE conditions). Only 8-10% need the most expensive model. Weighted average cost per query is ~$0.0036 — a 5-10x reduction vs using GPT-4o for every query ($0.02). Router accuracy target is >85%.

## Consequences

### Positive
- 50-70% cost reduction vs using GPT-4o for every query
- Self-hosted models reduce cloud API dependency
- Different models can be optimized independently
- Works in air-gapped deployments with self-hosted models

### Negative
- Router can misclassify (expensive query → cheap model → inaccurate result)
- Multiple models must be maintained and versioned (3 self-hosted + 1 cloud)
- Router accuracy directly affects cost and quality — must monitor and improve
- Router technology TBD (lightweight classifier in MVP, learned routing in Phase 2)

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Single model (GPT-4o for everything) | 3-10x cost, cloud API dependency, cannot air-gap |
| Single self-hosted model | Either too expensive for simple queries or too weak for complex ones |
| Rules-only routing | Fragile, doesn't adapt to query patterns |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Router misclassifies complex query as simple — generates wrong SQL | Medium | High | Validation agent catches wrong SQL; retry with higher-tier model; monitor classification accuracy by complexity tier |
| Self-hosted model (SQLCoder-7b) accuracy degrades on unseen domains | Medium | Medium | Regular accuracy evaluation against test suite; automatic fallback to higher tier if confidence < threshold |
| Router latency adds to end-to-end query time | Low | Medium | Router must complete in <50ms P99; pre-compute complexity features asynchronously when possible |
| Model registry drift (version mismatch between router and deployed models) | Medium | High | Model registry as source of truth (not hardcoded); health check on registration; stale model alerting |

## Trade-offs

- **4-tier routing vs 2-tier (simple vs complex)**: 4 tiers provide finer cost granularity but increase routing complexity and model maintenance burden. 2-tier would be simpler but would either overpay (medium queries to expensive model) or sacrifice quality (medium queries to cheap model). 4 tiers chosen for optimal cost-quality balance
- **Rule-based vs learned routing**: Rule-based routing (query length, JOIN count, subquery depth thresholds) is simpler to implement for MVP but does not adapt to query patterns. Learned routing (classifier trained on query-to-model outcomes) improves over time but requires training data and infrastructure. MVP starts with rule-based, transitions to learned routing in Phase 2
- **Self-hosted models vs cloud-only**: Self-hosted models (SQLCoder-7b, Qwen2.5-72B) reduce cloud API dependency and enable air-gapped deployment but require GPU infrastructure and model maintenance. Cloud-only would simplify operations but increase cost and violate deployment-agnostic principle

## Related ADRs

- ADR-009: Self-Hosted Inference Primary, Cloud Fallback (models run on self-hosted GPU or cloud fallback)
- ADR-015: GPU Vendor Strategy (GPU infrastructure for self-hosted models)

## References

- [Architecture-Review.md](../Architecture-Review.md) §10.8
- [Performance-Specification.md](../specifications/Performance-Specification.md) §4 (Inference Performance)
- [AI-Agent-Specification.md](../specifications/AI-Agent-Specification.md) §8 (Model Router Agent)
- [ModelRouter-Specification.md](../specifications/ModelRouter-Specification.md) §3 (Routing Strategies), §4 (Model Registry), §9 (Routing APIs)
