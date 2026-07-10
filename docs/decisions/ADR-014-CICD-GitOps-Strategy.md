# ADR-014: CI/CD and GitOps Strategy

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-014 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform must deliver changes across 5 environments (dev, staging, prod-SaaS, dedicated, on-prem) with reliability and speed. With 10+ microservices, 3 storage systems, and 5 deployment modes, the CI/CD pipeline must enforce quality gates, support gradual rollout (canary/blue-green), and enable rapid rollback. The pipeline must scale from 10 engineers to 100+.

## Decision

Use GitHub Actions for CI and ArgoCD for GitOps-based CD.

| Stage | Tool | Purpose |
|-------|------|---------|
| Source control | GitHub | Code review, branch protection, signed commits |
| CI pipeline | GitHub Actions | Build, lint, test, security scan, container build |
| Artifact registry | GitHub Container Registry (ghcr.io) | Immutable container images |
| CD (K8s) | ArgoCD | GitOps sync, automated deployment |
| CD (infra) | Terraform Cloud / OpenTofu | IaC state management, plan/apply |
| Feature flags | Environment variables (MVP) | Gradual feature rollout |
| Image builder | Docker BuildKit | Multi-stage, layer-cached builds |

## Rationale

- **GitHub Actions** is co-located with code (no external CI config), has the largest action ecosystem, and supports matrix builds for multi-arch/GPU testing
- **ArgoCD** enables true GitOps (desired state in Git, auto-sync, drift detection), supports progressive delivery (canary via Argo Rollouts), and has multi-cluster support for dedicated/VPC deployments
- **Docker BuildKit** provides parallel layer building, inline cache, and multi-platform builds (required for amd64 + arm64)
- **Immutable artifacts**: every commit produces a unique image SHA — no hot-patching, no configuration drift

## Consequences

### Positive
- Single CI system (GitHub Actions) — no context switching
- Git as single source of truth for infrastructure and application state
- Automatic drift detection (ArgoCD alerts if cluster state diverges from Git)
- Progressive delivery (canary 5%→25%→100%) with automated rollback on health failure
- Immutable artifacts enable deterministic rollbacks (revert Git commit)
- BuildKit caching reduces CI build time by 60-80% for unchanged layers

### Negative
- GitHub Actions minute costs grow linearly with team size and test volume
- ArgoCD sync conflicts when multiple PRs modify the same K8s manifest
- Git as deployment state means sensitive values must be externally managed (External Secrets)
- ArgoCD learning curve for engineers unfamiliar with GitOps
- CI pipeline becomes the bottleneck if test suite execution time grows unchecked

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| GitLab CI | Not using GitLab for source; dual-tool overhead |
| Jenkins | Legacy; high maintenance; no native GitOps support |
| CircleCI | Less integrated with GitHub; fewer self-hosted runner options |
| Flux (CD) | Less mature than ArgoCD; weaker multi-cluster support; no built-in progressive delivery |
| Manual kubectl apply | Error-prone; no audit trail; no rollback automation |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GitHub Actions runner capacity during peak builds | Medium | Medium | Self-hosted runners for GPU/performance builds; elastic scaling |
| ArgoCD sync conflicts on overlapping K8s changes | Medium | High | Branch-per-environment; sync waves; manual approval for concurrent manifests |
| Secrets exposed in CI logs | Low | Critical | Redact secrets in CI output; never echo env vars; use GitHub secret scanning |
| CI pipeline too slow for fast iteration | Medium | Medium | Parallel job execution; build caching; selective test execution (changed-file detection) |
| Rollback of DB-mutating deployments requires schema revert | Medium | High | Expand-contract migration pattern; no destructive DDL in automated deploy |

## Trade-offs

- **Centralized CI vs distributed agents**: GitHub Actions centralizes CI logic — simpler but creates single point of CI failure. Self-hosted runners mitigate availability risk
- **GitOps purity vs operational pragmatism**: True GitOps means no manual `kubectl exec` or port-forwarding. In practice, debugging requires temporary exceptions with strict timeout and audit
- **Immutable artifacts vs configuration flexibility**: Immutable images require configuration externalization (env vars, ConfigMaps). Pushing a config change requires updating ConfigMap + pod restart, not hot-reload
- **Pipeline speed vs safety**: Every quality gate (lint → test → security scan → build → deploy) adds minutes. Strategy: fast gates fail-fast (lint/typecheck < 2 min), slow gates (E2E/perf) run in parallel

## Related ADRs

- ADR-005: Self-Hosted Knowledge Stores Only (infrastructure provisioning)
- ADR-011: Technology Stack Selection (Docker, K8s, Terraform)
- ADR-012: Configuration Management Approach (secrets, ConfigMaps)
- ADR-013: Testing Framework Strategy (CI quality gates)

## References

- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §5 (CI/CD Pipeline), §6 (K8s Deployment)
- [Infrastructure-Specification.md](../specifications/Infrastructure-Specification.md) §4 (CI/CD Infrastructure)
- [Implementation-Plan.md](../Implementation-Plan.md) §5 (Quality Gates)
