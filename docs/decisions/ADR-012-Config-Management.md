# ADR-012: Configuration Management Approach

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-012 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Each service requires configuration (database URLs, API keys, model endpoints, feature flags). We need a unified approach across all 5 deployment modes (SaaS -> air-gapped) that works for local development, CI, staging, and production.

## Decision

We will use **Pydantic Settings** for all Python services with **environment variable overrides**, managed via **Kubernetes Secrets + ConfigMaps** in production.

- **Library**: `pydantic-settings` (built into Pydantic v2)
- **Config inheritance**: `BaseConfig` -> `DevConfig` -> `StagingConfig` -> `ProdConfig`
- **Secrets**: K8s External Secrets Operator (HashiCorp Vault or AWS Secrets Manager)
- **Feature flags**: Boolean environment variables, no external feature flag service in MVP

## Rationale

- **Pydantic Settings** provides type-safe configuration with env var override, `.env` file support, and validation
- **No separate config service** in MVP (adds complexity without sufficient benefit for < 100 tenants)
- **K8s External Secrets** enables cloud-agnostic secrets management (Vault in on-prem, AWS/GCP/Azure in cloud)
- **Environment variables** are the Kubernetes standard (ConfigMaps for non-sensitive, Secrets for sensitive)

## Consequences

### Positive
- Type-safe configuration with IDE autocomplete
- `.env` files work for local development without changes
- Works identically in all 5 deployment modes (env vars are universal)
- Secrets never in code or git
- Feature flags can be changed without redeployment (pod restart only)

### Negative
- Feature flag proliferation risk (need strict naming convention)
- No dynamic reload of config (requires pod restart)
- No centralized config audit (though K8s audit logging covers this)

## Configuration Schema (per service)

```python
# backend/shared/config.py
class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")
    
    # Service identity
    service_name: str
    service_port: int
    environment: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    
    # Database
    database_url: PostgresDsn
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # KE API (for non-KE services)
    ke_api_url: str = "http://ke-api:8200"
    ke_api_token: str
    
    # Qdrant (for KE service)
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_prefer_grpc: bool = True
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Feature flag proliferation without naming convention causes confusion | High | Medium | Strict naming convention: `FF_<SERVICE>_<FEATURE>_<YYYYMM>`; automated FF inventory; deprecation/cleanup policy |
| Secret rotation (90-day) causes deployment failures if not coordinated | Medium | Medium | External Secrets Operator handles rotation transparently; pods restart automatically with new secrets |
| Config drift between environments (dev vs prod values diverge) | Medium | High | Layered config files with clear override rules; environment-specific files in Git; ArgoCD drift detection |
| Large ConfigMap changes cause mass pod restart across services | Medium | Medium | ConfigMap immutability (new name per change); rolling update instead of delete/recreate; staged rollout |

## Trade-offs

- **Pydantic Settings vs external config service**: Pydantic Settings provides type-safe, validated configuration without a separate service dependency. An external config service (Consul, etcd) would enable dynamic reload without pod restart but adds infrastructure complexity and latency. Pydantic Settings chosen for MVP simplicity; config service evaluated at >50 services
- **Environment variables vs config files**: Environment vars are the Kubernetes standard, universally supported, and work in all 5 deployment modes. Config files enable more complex structures (nested config, arrays) but require file system access and complicate secret management. Env vars chosen for simplicity; config files for non-sensitive structured data only
- **External Secrets Operator vs Vault sidecar**: ESO provides Kubernetes-native secret management with reconciliation and rotation. Vault sidecar requires Vault infrastructure and agent configuration. ESO chosen for simpler deployment model; Vault as optional upgrade for on-prem/air-gapped deployments requiring HSM compliance

## Related ADRs

- ADR-003: Components Are Stateless Executors (configuration externalized per stateless principle)
- ADR-005: Self-Hosted Knowledge Stores Only (DB connection config varies by deployment mode)
- ADR-014: CI/CD and GitOps Strategy (ArgoCD manages ConfigMap/Secret lifecycle)

## References

- [Deployment-Architecture.md](../Deployment-Architecture.md) §5.6 (Configuration Management)
- [Component-Design.md](../Component-Design.md) §2.4 (Configuration)
- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §8 (Secrets Management), §9 (Configuration Management)
