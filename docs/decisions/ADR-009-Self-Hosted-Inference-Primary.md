# ADR-009: Self-Hosted Inference Primary, Cloud Fallback

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-009 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

LLM inference is the most computationally expensive operation in the platform. The choice between self-hosted inference (on AMD ROCm GPUs) and cloud API inference (GPT-4o, Claude) affects cost, latency, data privacy, and deployment flexibility.

## Decision

Self-hosted inference (vLLM/SGLang on AMD ROCm) as primary. Cloud APIs (GPT-4o/Claude) as fallback only for edge cases.

## Rationale

Self-hosted inference provides 20-30% cost advantage over cloud APIs at scale. No data leaves the deployment environment (compliance). Consistent latency characteristics (no cloud API variability). Works in all 5 deployment modes including air-gapped.

AMD MI300X (192GB HBM3) is the primary GPU target. vLLM and SGLang both support AMD ROCm 6.3+ with mature performance. The inference abstraction layer ensures hardware-agnostic operation (avoid CUDA lock-in).

## Consequences

### Positive
- 20-30% cost advantage over cloud APIs at production scale
- No data sent to third-party providers (compliance for regulated industries)
- Consistent latency (no cloud API variability)
- Works in air-gapped deployments
- GPU vendor independence via inference abstraction layer

### Negative
- GPU hardware acquisition cost (CAPEX vs OPEX)
- GPU management overhead (driver updates, model reloads, ROCm version management)
- Self-hosted models may have lower accuracy than latest GPT/Claude on complex queries
- Requires in-house GPU operations expertise

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Cloud API primary | Higher cost; data leaves premises; cannot air-gap |
| CPU inference only | Latency 10-100x worse for LLMs — unacceptable for interactive queries |
| NVIDIA-only GPU strategy | Vendor lock-in; higher cost; violates hardware-agnostic principle |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| vLLM/SGLang AMD ROCm compatibility regression blocks model serving | Medium | Critical | Pin ROCm + vLLM/SGLang versions in deployment; pre-deployment model health check; cloud fallback available during resolution |
| Self-hosted model accuracy lags behind GPT-4o/Claude for complex queries | Medium | Medium | Cloud fallback for complex queries (ADR-008 routing tier); regular model accuracy evaluation against test suite |
| GPU hardware failure during peak usage degrades query throughput | Low | High | GPU node pool with multiple nodes; automatic pod rescheduling; cloud API fallback if all GPUs fail |
| MI300X availability constraints delay production deployment | Medium | High | Pre-provision GPU nodes in target regions; maintain MI250/MI350 as alternative; cloud inference as interim |

## Trade-offs

- **Self-hosted vs cloud inference**: Self-hosted inference provides cost advantage (20-30% at scale), data privacy, and air-gapped support. Cloud inference provides instant access to latest models, zero GPU operations, and elastic scaling. The primary/secondary model (self-hosted primary, cloud fallback) balances both
- **vLLM vs SGLang**: vLLM has broader model support and larger community; SGLang offers structured generation (JSON mode) that is useful for SQL generation. Both support AMD ROCm. Chosen: primary = vLLM (broader support), secondary = SGLang (structured generation when needed), both in the inference abstraction layer
- **AMD ROCm vs CUDA**: ROCm avoids vendor lock-in and offers cost advantages but has less mature ecosystem. CUDA ecosystem is more mature with better tooling and larger talent pool. The abstraction layer provides optionality — deploy on either GPU vendor without component changes

## Related ADRs

- ADR-008: Tiered Model Routing (routing to self-hosted vs cloud models)
- ADR-015: GPU Vendor Strategy (AMD ROCm as primary GPU platform)

## References

- [Architecture-Review.md](../Architecture-Review.md) §10.9
- [Infrastructure-Specification.md](../specifications/Infrastructure-Specification.md) §5 (GPU Infrastructure)
- [Performance-Specification.md](../specifications/Performance-Specification.md) §4 (Inference Performance)
- [ModelRouter-Specification.md](../specifications/ModelRouter-Specification.md) §17 (Hardware Abstraction)
- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §12 (GPU Deployment), §13 (AMD ROCm Procedures)
