# ADR-015: GPU Vendor Strategy — AMD ROCm Primary, NVIDIA Roadmap

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-015 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform requires GPU inference for self-hosted LLMs (SQLCoder-7b, Qwen2.5-72B, DeepSeek-V3) as specified in ADR-009. The GPU vendor choice affects hardware cost per inference, software compatibility (vLLM/SGLang driver support), supply chain risk, data center power/cooling requirements, and strategic vendor independence. AMD MI300X and NVIDIA H100/B300 are the primary candidates for production LLM inference.

## Decision

AMD ROCm (MI300X) as the primary GPU platform. Phased NVIDIA (H100 → B300) support on the roadmap for customer-driven requirements.

| Phase | GPU | Timeline | Rationale |
|-------|-----|----------|-----------|
| V1.0 | AMD MI300X (192GB HBM3) | Launch | Best price/performance for inference; sufficient VRAM for DeepSeek-V3; no CUDA lock-in |
| V1.5 | AMD MI400-series evaluation | 3-6 months post-launch | Next-gen AMD with improved ROCm compatibility |
| V2.0 | NVIDIA H100 80GB | Customer demand | For customers with existing NVIDIA infrastructure; CUDA ecosystem compatibility |
| V2.5 | NVIDIA B300 192GB | Market availability | Blackwell architecture for high-throughput inference |

## Rationale

- **Total cost of inference**: AMD MI300X provides approximately 20-30% better price/performance vs NVIDIA H100 for LLM inference (based on published MLPerf Inference and independent benchmarks)
- **VRAM capacity**: MI300X (192GB HBM3) enables running DeepSeek-V3 (671B total, ~37B activated) without tensor parallelism across multiple GPUs — reduces networking cost and latency
- **Vendor independence**: Avoids CUDA lock-in — the inference abstraction layer (vLLM/SGLang with ROCm support) ensures hardware-agnostic model deployment
- **ROCm maturity**: AMD ROCm 6.3+ provides production-quality support for vLLM 0.6+ and SGLang 0.4+ with performance within 10-15% of CUDA for inference workloads
- **Supply chain diversity**: AMD offers better availability and shorter lead times than NVIDIA for data center GPUs

## Consequences

### Positive
- 20-30% inference cost advantage over NVIDIA-only strategy at production scale
- Vendor independence — no CUDA lock-in, no single-supplier risk
- MI300X 192GB enables running large models (DeepSeek-V3, Qwen2.5-72B) on single GPU — simpler deployment topology
- Dual-vendor roadmap provides negotiation leverage and supply chain resilience
- ROCm investment aligns with AMD's growing data center market share

### Negative
- ROCm software stack less mature than CUDA — occasional driver compatibility issues
- Smaller GPU operator talent pool (more engineers know CUDA than ROCm)
- NVIDIA B300 (2026) may offer compelling performance for inference — AMD must maintain parity
- Some ML frameworks and optimization libraries are CUDA-first (TensorRT, FlashAttention)
- Additional engineering effort for dual-vendor GPU abstraction and testing

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| NVIDIA-only | Vendor lock-in; higher cost per inference; single-supplier risk; violates hardware-agnostic principle |
| Intel Gaudi 3 | Immature software stack; poor vLLM/SGLang support; limited community adoption |
| Google TPU | Cloud-only — violates deployment-agnostic principle; cannot air-gap |
| AWS Trainium/Inferentia | Cloud-only; vendor lock-in; limited model compatibility |
| CPU inference only | 10-100x slower for LLMs — unacceptable for interactive query latency budget |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ROCm driver regression breaks model inference | Medium | Critical | Pin ROCm version in deployment; pre-deployment model validation in CI; rollback plan |
| AMD discontinues or deprioritizes ROCm consumer GPU support | Low | Medium | Server-grade only (MI300X); maintain abstraction layer for NVIDIA migration |
| NVIDIA B300 offers 50%+ better inference perf/watt | Medium | Medium | Dual-vendor roadmap; abstraction layer enables NVIDIA adoption in Phase 2 |
| Model requires CUDA-only optimization (e.g., FlashAttention-3) | Medium | High | Evaluate AMD Composable Kernel (CK) equivalents; fall back to standard attention |
| GPU talent: hard to hire engineers with ROCm experience | Medium | Low | Invest in team training; abstract GPU details behind inference service boundary |

## Trade-offs

- **ROCm cost savings vs ecosystem maturity**: AMD offers better price/performance today but NVIDIA has the mature software ecosystem. Trade-off favors AMD for cost-constrained inference workloads; NVIDIA may be preferred if customer demands CUDA ecosystem
- **Single GPU vs multi-GPU**: MI300X 192GB enables serving DeepSeek-V3 on a single GPU (no inter-GPU communication), simplifying deployment. However, NVIDIA H100 with NVLink enables faster multi-GPU inference. Single-GPU approach chosen for V1.0 simplicity
- **Inference abstraction cost**: The hardware-agnostic layer (vLLM/SGLang abstraction) adds ~5-10% engineering overhead but provides vendor optionality — cost justified by strategic independence
- **ROCm 6.3+ stability vs latest features**: Pinning ROCm version for stability means delayed access to latest AMD GPU features. Annual ROCm upgrade cycle balances stability with feature adoption

## Related ADRs

- ADR-008: Tiered Model Routing (inference endpoint abstraction)
- ADR-009: Self-Hosted Inference Primary, Cloud Fallback (self-hosted GPU inference)
- ADR-011: Technology Stack Selection (vLLM, SGLang)
- ADR-016: Observability and Monitoring Stack (GPU metrics, ROCm telemetry)

## References

- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §12 (GPU Deployment), §13 (AMD ROCm Procedures)
- [Infrastructure-Specification.md](../specifications/Infrastructure-Specification.md) §5 (GPU Infrastructure)
- [Performance-Specification.md](../specifications/Performance-Specification.md) §4 (Inference Performance)
- [ModelRouter-Specification.md](../specifications/ModelRouter-Specification.md) §17 (Hardware Abstraction)
