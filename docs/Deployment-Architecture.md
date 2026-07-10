# Deployment Architecture

**Enterprise Data Intelligence Platform — Phase 2 Architecture & Design**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [System-Architecture.md](./System-Architecture.md), [Knowledge-Engine.md](./Knowledge-Engine.md), [Component-Design.md](./Component-Design.md), [API-Design.md](./API-Design.md), [Data-Flow.md](./Data-Flow.md) |

---

## 1. Deployment Principles

| Principle | Implication |
|-----------|-------------|
| **Cloud-agnostic** | Kubernetes + Terraform. No managed service lock-in for core infrastructure. |
| **Self-hosted everything** | No external API dependencies for core functionality. All knowledge stores are self-hosted. |
| **Five deployment modes** | Same architecture, same Docker images, different config. |
| **Stateless services** | All components are stateless. State lives in Knowledge Engine stores. Scale horizontally by adding pods. |
| **Infrastructure as Code** | Everything in Terraform. Reproducible environments. GitOps deployment. |

---

## 2. Kubernetes Cluster Architecture

### 2.1 Node Pools

```
┌─────────────────────────────────────────────────────────────┐
│                   KUBERNETES CLUSTER                         │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ System     │  │ General    │  │ GPU        │             │
│  │ (3-5 nodes)│  │ Purpose    │  │ (1-8 nodes)│             │
│  │ 4 vCPU     │  │ (3-10)     │  │ MI300X /   │             │
│  │ 16GB RAM   │  │ 8 vCPU     │  │ H100       │             │
│  │            │  │ 32GB RAM   │  │ 192GB VRAM │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│  • Istio mesh    │  • API Layer   │  • vLLM                │
│  • Cert-manager  │  • Pipeline    │  • SGLang              │
│  • Monitoring    │    Components  │  • Embedding service   │
│  • PostgreSQL    │  • PG Pooler   │                         │
│  • Qdrant        │  • Learning    │                         │
│  • Redis         │    Loop        │                         │
│  • Ingress       │               │                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Namespace Layout

| Namespace | Purpose | Resource Quota |
|-----------|---------|----------------|
| `system` | Istio, cert-manager, monitoring, logging | High |
| `knowledge-engine` | PostgreSQL, Qdrant, Redis, KE API | High (persistent storage) |
| `pipeline` | Query Analyzer, Retriever, Planner, NL2SQL, Guardrails, Executor | Medium |
| `learning` | Learning Loop, Schema Intelligence | Medium |
| `api` | Public API, Auth proxy | Medium |
| `gpu` | vLLM, SGLang, Embedding service | GPU-bound |
| `tenants` | Per-tenant sidecars or agent pools (future) | Medium |

---

## 3. Component Service Map

| Component | Service Name | Replicas (MVP) | CPU/Mem Request | CPU/Mem Limit | Scaling |
|-----------|-------------|----------------|-----------------|---------------|---------|
| API Layer | `api-gateway` | 2 | 0.5/512Mi | 2/2Gi | CPU > 70% |
| Query Analyzer | `query-analyzer` | 2 | 0.5/1Gi | 2/4Gi | CPU > 70% |
| Context Retriever | `context-retriever` | 2 | 0.5/1Gi | 2/4Gi | CPU > 70% |
| Query Planner | `query-planner` | 2 | 0.5/1Gi | 2/4Gi | CPU > 70% |
| NL2SQL Generator | `nl2sql-generator` | 3 | 1/2Gi | 4/8Gi | Queue depth > 10 |
| Policy Enforcement | `policy-enforcement` | 2 | 0.5/1Gi | 2/2Gi | CPU > 70% |
| Executor | `query-executor` | 3 | 0.5/1Gi | 2/4Gi | Connection pool pressure |
| Schema Intelligence | `schema-intelligence` | 1 | 1/2Gi | 4/8Gi | Event-triggered (not load) |
| Learning Loop | `learning-loop` | 1 | 1/2Gi | 4/8Gi | Batch (not load) |
| Feedback Collector | `feedback-collector` | 1 | 0.5/512Mi | 1/2Gi | Event-triggered |
| Knowledge Engine API | `knowledge-engine` | 2 | 1/2Gi | 4/8Gi | CPU > 70% |
| vLLM Server | `vllm-server` | 1 per GPU | 4/16Gi | GPU: 1 | GPU utilization > 80% |
| SGLang Server | `sglang-server` | 1 | 4/16Gi | GPU: 1 | Request volume |
| Embedding Service | `embedding-service` | 1 | 2/4Gi | GPU: 1 | Batch queue depth |

---

## 4. Storage Architecture

### 4.1 PostgreSQL

| Component | Configuration | Storage |
|-----------|--------------|---------|
| **Engine** | PostgreSQL 16 with `pgvector` extension | — |
| **HA Mode** | Patroni (streaming replication, 1 primary + 2 replicas) | — |
| **Primary** | 8 vCPU, 32GB RAM, 500GB SSD (GP3) | Read-write |
| **Replica 1** | 8 vCPU, 32GB RAM, 500GB SSD | Read-only queries |
| **Replica 2** | 4 vCPU, 16GB RAM, 500GB SSD | Analytics/reporting queries |
| **Connection pooling** | PgBouncer (per-tenant connection limits) | — |
| **Backups** | pgBackRest, daily full + WAL archiving (30-day retention) | S3-compatible storage |
| **Failover** | Automatic via Patroni (RPO: <1MB, RTO: <30s) | — |

### 4.2 Qdrant

| Component | Configuration | Storage |
|-----------|--------------|---------|
| **Engine** | Qdrant 1.12+ (self-hosted) | — |
| **Nodes** | 3-node cluster | — |
| **Node spec** | 4 vCPU, 16GB RAM, 200GB NVMe | Local SSD |
| **Replication** | Factor: 2 (per collection) | — |
| **Sharding** | Auto-shard across nodes per collection size | — |
| **Backups** | Snapshot to S3 daily | — |

### 4.3 Redis

| Component | Configuration |
|-----------|--------------|
| **Engine** | Redis 7+ (self-hosted, HA via sentinel) |
| **Purpose** | Cache (schema, RBAC, resolutions), rate limiting, task queues |
| **Nodes** | 3-node sentinel cluster |
| **Node spec** | 2 vCPU, 4GB RAM |
| **Persistence** | AOF fsync every 1s (cache loss acceptable; hot reload from PG) |

---

## 5. Multi-Tenancy Model

### 5.1 Isolation Strategy

| Layer | Strategy | Rationale |
|-------|----------|-----------|
| **Data** | Row-level tenant IDs in shared PostgreSQL tables. Per-tenant Qdrant collections. | Most cost-effective. Still fully isolated at query level. |
| **Performance** | Kubernetes resource quotas + per-tenant cost ceilings + query priority queues. | No noisy-neighbor problems at moderate scale. |
| **Security** | Tenant ID in every API call (JWT claim). Verified by API Layer before forwarding. | Impossible for Tenant A to access Tenant B's data even with wrong config. |
| **Inference** | Shared GPU pool with fair scheduling. Premium tenants get dedicated GPU pods. | Cost efficiency for majority; performance guarantee for premium. |
| **Configuration** | Per-tenant configuration records in Configuration Store. | Fully customizable per tenant. |

### 5.2 Tenant Data Flow

```
User Request
    │
    ▼
API Layer extracts tenant_id from JWT
    │
    ▼
All downstream requests include tenant_id header
    │
    ▼
Knowledge Engine filters all queries by tenant_id
    │
    ▼
PostgreSQL: WHERE tenant_id = 'uuid'
Qdrant: filter by payload.tenant_id = 'uuid'
```

### 5.3 Tenant Tiers and Resource Allocation

| Tier | Max Databases | Max Tables | Query Quota | GPU Priority | Storage Quota | Max Connections |
|------|--------------|------------|-------------|--------------|---------------|-----------------|
| Free | 1 | 10 | 100/mo | None (lowest priority) | 500MB | 5 |
| Starter | 3 | 100 | 200/seat/mo | Best-effort | 2GB | 10 |
| Pro | 10 | 500 | 1,000/seat/mo | Normal | 10GB | 25 |
| Enterprise | Unlimited | Unlimited | Custom | Dedicated (optional) | Custom | Custom |

---

## 6. Deployment Modes

### 6.1 Mode Comparison

```
                  Cloud SaaS    Dedicated      VPC         On-Prem K8s    Air-Gapped
                  ─────────     ─────────     ───         ──────────     ─────────
K8s Cluster       Shared        Per-tenant    Customer's  Customer's     Customer's
PostgreSQL        Shared PG     Per-tenant    Customer's  Customer's     Customer's
                  (row-level)   PG instance   PG          PG             PG
Qdrant            Shared        Per-tenant    Customer's  Customer's     Customer's
                  (collection)  Qdrant node   Qdrant      Qdrant         Qdrant
GPU Inference     Shared GPU    Dedicated     Customer    Customer's     Customer's
                  pool          GPU pool      GPU (opt.)  GPU            GPU
Cloud Fallback    Yes           Yes           Yes (opt.)  No             No
LLMs              Self-hosted   Self-hosted   Self-hosted Self-hosted    Self-hosted
                  + fallback    + fallback    + fallback
External API      Yes           Yes           Yes (opt.)  No             No
Dependencies                                                          
Updates           Continuous    Scheduled     Scheduled   Manual         Manual
Support           Standard      Priority      Premium     Premium        Premium
```

### 6.2 Cloud SaaS (Default — MVP+)

```
[Internet]
    │
    ▼
[Cloudflare / CDN]
    │
    ▼
[Ingress (Istio Gateway)]
    │
    ▼
[API Layer] ──► [Auth0/Clerk]
    │
    ▼
[Service Mesh (Istio)]
    │
    ├── [Pipeline Services] ──► [KE API] ──► [PostgreSQL + Qdrant]
    │                                              │
    └── [GPU Pool] ──► [vLLM + SGLang]             │
                                                   │
    Customer Database ◄── [Executor] ◄──────────────┘
```

**Key differentiator from traditional SaaS**: The Knowledge Engine is self-hosted within our K8s cluster, not a cloud-managed service. This ensures deployment portability.

### 6.3 Dedicated Cloud (Phase 2)

```
Per-tenant namespace within shared K8s cluster
    │
    ├── Dedicated PostgreSQL instance
    ├── Dedicated Qdrant node
    ├── Shared GPU pool (or dedicated for premium)
    └── All pipeline services shared (stateless)
```

### 6.4 Customer VPC (Phase 3)

```
Customer's Cloud Account
    │
    ▼
[Customer's VPC]
    │
    ├── [Our K8s Cluster (EKS/GKE/AKS)]
    │   ├── Pipeline Components (stateless)
    │   ├── Knowledge Engine (PostgreSQL + Qdrant)
    │   └── GPU Pool (customer's choice)
    │
    ├── [Customer's Databases] ← internal network
    │
    └── [Tunnel/VPN] ──► [Our Control Plane]
                        (monitoring, updates, support)
```

### 6.5 On-Prem K8s (Phase 4)

```
Customer's Data Center
    │
    ▼
[Customer's K8s Cluster]
    │
    ├── All components self-contained
    ├── No external network dependency
    ├── Customer-managed GPU (AMD/NVIDIA)
    └── Air-gap ready (optional)
```

### 6.6 Air-Gapped (Phase 5)

Same as On-Prem, plus:
- All container images pre-loaded in private registry
- No DNS resolution to external hosts
- No license check connectivity
- All LLM model weights shipped on storage media

---

## 7. Networking

### 7.1 Internal Service Communication

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Service A│────►│ Service B│────►│ Service C│
│ (Pod)    │     │ (Pod)    │     │ (Pod)    │
└──────────┘     └──────────┘     └──────────┘
       │               │               │
       │               │               │
       ▼               ▼               ▼
   Istio sidecar   Istio sidecar   Istio sidecar
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
               mTLS (mutual TLS)
               Automatic encryption
               Service identity verification
```

### 7.2 External Database Connectivity

```
[Executor Pod]
    │
    ▼
[Egress Gateway (Istio)]
    │
    ├── TLS to customer database
    ├── IP allowlisting
    ├── Connection pooling (PgBouncer sidecar)
    └── Audit logging of all connections
```

### 7.3 Ingress

| Traffic | Entry Point | TLS | Auth |
|---------|-------------|-----|------|
| Public API | Cloudflare → Istio Gateway | Auto (Let's Encrypt) | JWT + rate limit |
| Web UI | Cloudflare → Istio Gateway | Auto | JWT + session |
| Webhook (Slack/Teams) | Cloudflare → Istio Gateway | Auto | HMAC signing |
| Internal health | Cluster-internal | mTLS | Service account |

---

## 8. CI/CD Pipeline

### 8.1 Pipeline Stages

```
[Developer Push]
    │
    ▼
[Build & Test]
    ├── Unit tests (pytest, vitest)
    ├── Integration tests (docker-compose)
    ├── Lint (ruff, ESLint)
    └── Type check (mypy, tsc)
    │
    ▼
[Container Build]
    ├── Docker build (multi-arch: amd64 + arm64)
    ├── Container scan (Trivy)
    └── Push to registry
    │
    ▼
[Staging Deploy]
    ├── Terraform plan
    ├── Helm deploy to staging cluster
    ├── Integration tests against staging
    └── Smoke tests (10 benchmark queries)
    │
    ▼
[Production Deploy]
    ├── Terraform apply (infra changes)
    ├── Helm deploy (rolling update)
    ├── Canary: 10% traffic → watch metrics (5 min)
    ├── Ramp: 50% → watch metrics (5 min)
    └── Full: 100% → confirm
    │
    ▼
[Monitor]
    ├── Error rate < 0.1% increase
    ├── Latency P95 < 10% increase
    └── Guardrail pass rate stable
```

### 8.2 Deployment Cadence

| Phase | Frequency | Rollout Strategy |
|-------|-----------|------------------|
| MVP (Year 1) | Weekly | Rolling update |
| Growth (Year 2) | Every 2-3 days | Canary (10% → 50% → 100%) |
| Scale (Year 3+) | Multiple times/day | Blue/green with instant rollback |

### 8.3 Rollback

- Automated rollback on: error rate > 1% increase, P95 latency > 20% increase, policy enforcement failure rate > 2x baseline
- Rollback time target: < 5 minutes from detection
- Git revert → CI/CD redeploys previous image

---

## 9. Observability Stack

### 9.1 Components

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | System metrics, business metrics |
| Logging | Grafana Loki (or ELK) | Structured log aggregation |
| Tracing | OpenTelemetry + Jaeger/Tempo | Distributed trace correlation |
| Alerting | Grafana Alertmanager | PagerDuty, Slack, email |
| Dashboards | Grafana | Per-service, per-tenant, business |
| Uptime | Checkly / synthetic monitors | External monitoring |

### 9.2 Key Dashboards

| Dashboard | Audience | Content |
|-----------|----------|---------|
| **System Health** | On-call | CPU/mem/disk per node + service, error rates, latency |
| **Query Pipeline** | Engineering | Per-stage latency, throughput, error rate, model routing distribution |
| **Knowledge Engine** | ML Team | Embedding latency, store query latency, ingestion throughput |
| **Guardrail** | Security | Block rate per layer, false positive/negative trends, top blocked resources |
| **Business** | CEO/Sales | Active users, queries/day, ARR, churn precursors, conversion funnel |
| **Tenant Health** | Support | Per-tenant: query count, error rate, storage usage, cost |

### 9.3 Critical Alerts

| Alert | Condition | Response Time |
|-------|-----------|---------------|
| API P95 latency > 5s | 5-minute sliding window | < 15 min |
| Error rate > 2% | 5-minute window | < 15 min |
| Guardrail false negative | Any occurrence | < 5 min (security incident) |
| Disk space > 80% | PostgreSQL or Qdrant | < 1 hour |
| GPU pod down | Any GPU pod unavailable | < 15 min |
| Knowledge Engine API down | All replicas unavailable | < 5 min (page) |

---

## 10. Infrastructure Cost Model

### 10.1 Monthly Cost Estimates (Cloud SaaS — 100 tenants)

| Component | MVP (Yr 1, 25 tenants) | Growth (Yr 2, 150 tenants) | Scale (Yr 3, 500 tenants) |
|-----------|------------------------|----------------------------|---------------------------|
| K8s control plane | $150 (EKS/GKE/AKS) | $150 | $150 |
| System nodes (3-5) | $500 | $1,000 | $2,000 |
| General purpose nodes (3-10) | $1,000 | $2,500 | $5,000 |
| GPU nodes (1-8) | $2,000 (2x MI300X) | $4,000 (4x MI300X) | $8,000 (8x MI300X) |
| PostgreSQL (HA) | $300 (3x 500GB) | $600 (3x 1TB) | $1,200 (3x 2TB) |
| Qdrant (3-node) | $500 | $1,000 | $2,000 |
| Redis (3-node) | $100 | $200 | $400 |
| Storage (EBS/PV) | $200 | $500 | $1,000 |
| Network (egress) | $100 | $500 | $1,500 |
| Cloud API inference | $200 | $800 | $2,000 |
| Monitoring infra | $100 | $200 | $400 |
| **Total monthly** | **~$5,150** | **~$11,450** | **~$23,650** |
| **Per-tenant monthly** | **$206** | **$76** | **$47** |

### 10.2 Cost Optimization Levers

| Lever | Impact | Timeline |
|-------|--------|----------|
| Spot/preemptible GPU instances | 60-70% GPU cost reduction | Phase 1 (with checkpointing) |
| AMD ROCm vs NVIDIA | 20-30% cost advantage | Phase 0 (already decided) |
| Tiered model routing | 50-70% inference cost reduction | MVP |
| Schema-level caching | Reduce redundant retrieval | MVP |
| GPU sharing (multi-model on single GPU) | 2-4x GPU utilization | Phase 1 |
| Read replica offloading | Reduce primary PG load | Phase 1 |
| Long-term compute commitments | 30-50% discount (1yr commit) | Phase 2 |

---

## 11. Disaster Recovery

| Scenario | RPO | RTO | Recovery Strategy |
|----------|-----|-----|-------------------|
| Single pod failure | 0 | <30s | K8s auto-restart |
| Single node failure | 0 | <2min | Pod rescheduling |
| AZ outage (cloud) | <5min | <15min | Multi-AZ cluster, PG streaming replicas |
| Region outage | <24h | <4h | Cross-region PG replication + Qdrant snapshots |
| Data corruption | <24h | <4h | Point-in-time recovery from backup |
| Full cluster loss | <24h | <24h | Terraform reprovision + backup restore |

---

## 12. References

| Source | Relevance |
|--------|-----------|
| [System-Architecture.md](./System-Architecture.md) | Component architecture deployed on this infrastructure |
| [Knowledge-Engine.md](./Knowledge-Engine.md) | Storage requirements for PostgreSQL + Qdrant |
| [Component-Design.md](./Component-Design.md) | Resource requirements per component |
| [Technology-Recommendations.md](../Technical-Landscape/Technology-Recommendations.md) | Technology justification for infrastructure choices |
