# Technology Recommendations

**Enterprise Data Intelligence Platform — Phase 0 Discovery**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 0.1 |
| **Cross-References** | [Technical-Landscape-Report.md](./Technical-Landscape-Report.md), [Research-Summary.md](./Research-Summary.md) |

---

## Table of Contents

1. [Overview](#1-overview)
2. [MVP Technology Stack](#2-mvp-technology-stack)
3. [Inference Strategy](#3-inference-strategy)
4. [Database Connectivity](#4-database-connectivity)
5. [Vector Store Selection](#5-vector-store-selection)
6. [Agent Framework Selection](#6-agent-framework-selection)
7. [LLM Selection](#7-llm-selection)
8. [Backend Framework](#8-backend-framework)
9. [Frontend Technology](#9-frontend-technology)
10. [Infrastructure](#10-infrastructure)
11. [Security & Compliance](#11-security--compliance)
12. [Monitoring & Observability](#12-monitoring--observability)
13. [CI/CD & Development Workflow](#13-cicd--development-workflow)
14. [Phase 2 Additions](#14-phase-2-additions)
15. [Technology Radar](#15-technology-radar)

---

## 1. Overview

This document captures the specific technology recommendations derived from the Technical Landscape Report. Each recommendation includes rationale, alternatives considered, and decision criteria.

### Decision Framework

Each recommendation follows this structure:

```
Technology: [Name]
Status: [Adopt / Trial / Assess / Hold]
Rationale: [Why this technology]
Alternatives Considered: [Other options evaluated]
Decision Criteria: [What would cause us to change]
```

### Recommendation Status Definitions

| Status | Meaning |
|--------|---------|
| **Adopt** | Proven technology for this use case. Use in production. |
| **Trial** | Promising but needs validation. Use in non-critical paths. |
| **Assess** | Worth evaluating. Not yet recommended for production. |
| **Hold** | Not recommended at this time. |

---

## 2. MVP Technology Stack

| Category | Technology | Status | Phase |
|----------|-----------|--------|-------|
| Backend Framework | Python 3.12 + FastAPI | **Adopt** | MVP |
| Agent Orchestration | LangGraph | **Adopt** | MVP |
| Database Abstraction | SQLAlchemy 2.0 + Alembic | **Adopt** | MVP |
| Vector Store | Qdrant (self-hosted, K8s) | **Adopt** | MVP |
| Relational Store | PostgreSQL 16 | **Adopt** | MVP |
| Cache | Redis 7 | **Adopt** | MVP |
| Message Queue | Redis Streams / RabbitMQ | **Trial** | MVP |
| LLM Inference (Self-hosted) | vLLM (ROCm) | **Adopt** | MVP |
| LLM Inference (Agent) | SGLang (ROCm) | **Adopt** | MVP |
| LLM Inference (Cloud) | OpenAI / Anthropic API | **Adopt** | MVP |
| Primary Models | Qwen2.5-72B + SQLCoder-7b | **Adopt** | MVP |
| Embedding Model | BGE-M3 | **Adopt** | MVP |
| Auth / Identity | Auth0 | **Adopt** | MVP |
| Frontend | React 19 + Next.js 15 | **Adopt** | MVP |
| UI Components | shadcn/ui + Tailwind CSS | **Adopt** | MVP |
| Container Runtime | Docker + Kubernetes | **Adopt** | MVP |
| IaC | Terraform | **Adopt** | MVP |
| CI/CD | GitHub Actions | **Adopt** | MVP |
| Observability | OpenTelemetry + Grafana + Loki + Tempo | **Adopt** | MVP |
| Secret Management | HashiCorp Vault / AWS Secrets Manager | **Adopt** | MVP |
| API Gateway | Kong / Envoy | **Trial** | V1 |
| Graph Database | Neo4j | **Assess** | Phase 2 |
| Knowledge Graph Engine | FalkorDB | **Assess** | Phase 2 |
| Fine-Tuning Framework | Axolotl + Unsloth | **Assess** | Phase 2 |
| MCP Server | Custom (MCP protocol) | **Assess** | Phase 2 |

---

## 3. Inference Strategy

### 3.1 Tiered Model Routing

```
┌──────────────┐     ┌──────────────────┐
│  Question    │────▶│  Router Model    │
│              │     │  (Qwen2.5-7B)    │
└──────────────┘     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │   Simple    │ │   Medium    │ │   Complex   │
      │ SQLCoder-7b │ │ DeepSeek-V3 │ │ GPT-4o/     │
      │ (< $0.001)  │ │ (< $0.005)  │ │ Claude      │
      │             │ │             │ │ (< $0.02)   │
      └─────────────┘ └─────────────┘ └─────────────┘
```

| Tier | Expected % of Queries | Model | Latency | Cost/Query | Inference Engine |
|------|----------------------|-------|---------|------------|-----------------|
| Simple | 65% | SQLCoder-7b (INT4) | <500ms | <$0.001 | vLLM (ROCm) |
| Medium | 25% | DeepSeek-V3 / Qwen2.5-72B | <2s | <$0.005 | vLLM (ROCm) |
| Complex | 8% | GPT-4o / Claude 3.5 Sonnet | <5s | <$0.02 | Cloud API |
| Edge | 2% | GPT-4o / Claude 3 Opus | <10s | <$0.05 | Cloud API + fallback |

### 3.2 Hardware Plan

| Phase | Hardware | Models | Estimated Capacity | Monthly Cost (Amortized) |
|-------|----------|--------|-------------------|--------------------------|
| MVP (Q1) | 2x MI300X (192GB) | SQLCoder-7b + Qwen2.5-72B | 5K QPD | $4,000-6,000 |
| Growth (Q2) | 4x MI300X (192GB) | + DeepSeek-V3 | 20K QPD | $8,000-12,000 |
| Scale (Q3) | 8x MI300X + cloud burst | All tiers | 50K QPD | $15,000-25,000 |

### 3.3 Provider Abstraction

**Status: Adopt — Build custom lightweight layer**

```python
# Core abstraction (MVP)
class InferenceProvider(ABC):
    """Abstract base for all inference providers."""
    
    @abstractmethod
    async def chat(
        self, 
        model: str, 
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: int = 4096,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> InferenceResult: ...
    
    @abstractmethod
    async def embed(
        self, 
        model: str, 
        texts: list[str]
    ) -> list[list[float]]: ...

# Implementations:
# - VLLMProvider (self-hosted AMD GPUs via vLLM API)
# - SGLangProvider (self-hosted AMD GPUs via SGLang API)
# - OpenAIProvider (cloud fallback)
# - AnthropicProvider (cloud fallback)
# - OllamaProvider (local dev/test)
```

**Rationale**: Prevents GPU vendor lock-in. Allows seamless fallback to cloud APIs during AMD provisioning delays. Enables cost optimization by routing to cheapest provider that meets accuracy requirements.

**Alternatives Considered**:
- **LiteLLM**: Mature proxy, but assumes cloud APIs. Limited self-hosted support.
- **OpenRouter**: Managed API gateway. Vendor lock-in, data leaves our control.
- **Custom solution (chosen)**: Maximum flexibility, minimal dependencies, full control over routing logic.

---

## 4. Database Connectivity

### 4.1 MVP Dialect Support

| Dialect | Connector | Status | Notes |
|---------|-----------|--------|-------|
| PostgreSQL | asyncpg + SQLAlchemy | **Adopt** | Primary reference dialect |
| MySQL | aiomysql + SQLAlchemy | **Adopt** | Requires special handling for LIMIT/OFFSET |
| Snowflake | snowflake-connector-python | **Adopt** | Requires OAuth/IAM for enterprise |
| BigQuery | google-cloud-bigquery | **Adopt** | Requires GCP service account |
| DuckDB | duckdb (embedded) | **Adopt** | Dev/test, embedded use cases |

### 4.2 Phase 2 Dialects

| Dialect | Connector | Status | Priority |
|---------|-----------|--------|----------|
| Microsoft SQL Server | pyodbc + SQLAlchemy | **Assess** | High (enterprise demand) |
| Oracle | oracledb + SQLAlchemy | **Assess** | High (legacy systems) |
| Amazon Redshift | redshift-connector | **Assess** | Medium |
| ClickHouse | clickhouse-driver | **Assess** | Medium |
| Databricks SQL | databricks-sql-connector | **Assess** | Medium |

### 4.3 Connector Architecture

**Status: Adopt — Pluggable connector pattern**

```
┌─────────────────────────────────────────────┐
│            DatabaseConnector (ABC)           │
├─────────────────────────────────────────────┤
│ + introspect_schema() → SchemaMetadata       │
│ + execute_query(sql, params) → QueryResult   │
│ + test_connection() → bool                   │
│ + get_dialect_info() → DialectInfo           │
│ + get_query_history(limit) → list[QueryLog]  │
└─────────────────────────────────────────────┘
                    ▲
    ┌───────────────┼───────────────┐
    │               │               │
┌───────┐     ┌─────────┐     ┌──────────┐
│ PG    │     │ Snowflake│     │ BigQuery │
│Connector│   │Connector │     │Connector  │
└───────┘     └─────────┘     └──────────┘
```

**Rationale**: Each dialect has unique auth, data type mapping, and SQL syntax characteristics. A shared interface allows the NL2SQL pipeline to be dialect-agnostic while each connector handles dialect-specific complexity.

---

## 5. Vector Store Selection

### 5.1 Decision: Qdrant (Self-Hosted)

| Criteria | Qdrant | pgvector | Milvus | Pinecone |
|----------|--------|----------|--------|----------|
| **Filtered Search** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★☆ |
| **Latency (p99)** | 18ms | 58ms | 25ms | 22ms |
| **Throughput** | 42K vec/s | 12K vec/s | 38K vec/s | 18K vec/s |
| **Self-Hosted** | Yes | Yes (in Postgres) | Yes | No |
| **ROCm Compatible** | Yes (Docker) | Yes | Yes | N/A |
| **Cost (100M vec)** | ~$280/mo | ~$180/mo | ~$310/mo | ~$650/mo |
| **Multi-Tenancy** | Built-in | Via row-level | Via collections | Via namespaces |
| **Rust (Performance)** | Yes | No (C/Postgres) | Go/C++ | Proprietary |

**Rationale**: Qdrant wins on the most important criterion — filtered search performance. Enterprise NL2SQL requires heavy metadata filtering (by tenant, schema, date, status). Qdrant's Rust implementation provides the best price/performance ratio.

**Alternatives Considered**:
- **pgvector**: Lowest cost, simplest stack (same DB as metadata), but performance degrades past 10M vectors and at high concurrency.
- **Milvus**: Better at extreme scale (1B+ vectors), but over-engineered for our scale and more complex to operate.
- **Pinecone**: Best managed UX but 2x+ cost and no self-hosting option (data privacy concern for enterprise).

### 5.2 Collection Structure

| Collection | Purpose | Vector Dim | Index | Filter Fields |
|------------|---------|------------|-------|---------------|
| `table_ddls` | DDL statement embeddings | 1024 | HNSW | tenant_id, db_type |
| `column_descriptions` | Column-level meaning | 1024 | HNSW | tenant_id, table_id |
| `qa_pairs` | Successful Q&A examples | 1024 | HNSW | tenant_id, category |
| `documentation` | Business docs, wikis | 1024 | HNSW | tenant_id, source |
| `query_history` | Historical queries + patterns | 1024 | HNSW | tenant_id, user_id |

---

## 6. Agent Framework Selection

### 6.1 Decision: LangGraph

| Criteria | LangGraph | CrewAI | AutoGen | DB-GPT |
|----------|-----------|--------|---------|--------|
| **DAG + Cycles** | Native | Limited | Limited | DAG support |
| **Conditional Branching** | Yes | Limited | Via agents | Yes (AWEL) |
| **Human-in-the-Loop** | Yes (interrupt) | No | Yes | No |
| **LangSmith Observability** | Yes | No | Limited | No |
| **Streaming** | Yes | Limited | Yes | Yes |
| **Maturity** | High | Medium | High | Medium |
| **NL2SQL-Specific** | No (generic) | No (generic) | No (generic) | Yes (purpose-built) |
| **Python Ecosystem** | Excellent | Good | Good | Limited (Chinese docs) |
| **License** | MIT | MIT | MIT | MIT |

**Rationale**: LangGraph provides the most flexible agent orchestration model (DAG + cycles + conditional branching), which maps exactly to the NL2SQL pipeline (plan → execute → validate → repair loop). Its LangSmith integration provides built-in observability for debugging complex agent interactions. The MIT license is enterprise-friendly.

**Alternatives Considered**:
- **CrewAI**: Simpler API, good for straightforward pipelines, but lacks the cycle support needed for the reflector/repairer loop.
- **AutoGen**: Strong code generation capabilities, but more focused on agent-to-agent conversation than structured pipeline execution.
- **DB-GPT**: Purpose-built for NL2SQL with AWEL workflow engine, but documentation is primarily in Chinese, community is China-centric, and framework dependencies are heavy.

---

## 7. LLM Selection

### 7.1 Primary Models

| Role | Model | Size | Quantization | VRAM | Inference Engine |
|------|-------|------|-------------|------|-----------------|
| Router/Classifier | Qwen2.5-7B-Instruct | 7B | INT4 (AWQ) | 8GB | vLLM (ROCm) |
| Simple SQL | SQLCoder-7b-2 | 7B | INT4 (AWQ) | 8GB | vLLM (ROCm) |
| Medium SQL | Qwen2.5-72B-Instruct | 72B | FP8 | 80GB (1x MI300X) | vLLM (ROCm) |
| Complex SQL | DeepSeek-V3 | 671B (MoE, 37B active) | FP8 | ~192GB (1-2x MI300X) | SGLang (ROCm) |
| Embedding | BGE-M3 | 567M | FP16 | 4GB | vLLM (ROCm) |

### 7.2 Cloud Fallback Models

| Role | Model | When Used |
|------|-------|-----------|
| Hard queries | GPT-4o / Claude 3.5 Sonnet | Router confidence < 0.8 on all self-hosted candidates |
| Edge cases | Claude 3 Opus | First attempt failed, unusual query pattern |
| Batch analysis | GPT-4o-mini | Low-cost bulk processing |

### 7.3 Fine-Tuning Roadmap

| Phase | Model | Training Data | Expected Improvement |
|-------|-------|--------------|---------------------|
| V1 | SQLCoder-7b (LoRA) | Customer Q&A pairs + public SQL datasets | +5-10% on domain-specific queries |
| V2 | Qwen2.5-72B (LoRA) | Accumulated query logs + validated pairs | +10-15% overall |
| V3 | Domain-specific models | Industry-specific datasets (fintech, healthcare, etc.) | +15-20% on vertical queries |

### 7.4 Selection Rationale

**SQLCoder-7b-2**: Chosen for the simple tier because:
- Outperforms GPT-4 on complex ratio queries (91.4% vs 80%)
- Small (7B) → fits on single GPU even with quantization
- Apache 2.0 license
- Fine-tuned specifically for SQL generation

**Qwen2.5-72B**: Chosen for the medium tier because:
- Strong all-around performance on text-to-SQL
- Excellent ROCm support (Alibaba has been a primary AMD partner)
- 128K context window (handles large schema context)
- Apache 2.0 license

**DeepSeek-V3**: Chosen for the complex tier because:
- MoE architecture (37B active params) provides GPT-4-class quality at much lower cost
- SGLang has first-class DeepSeek optimization with ROCm
- Excellent at complex reasoning and multi-join queries

**BGE-M3**: Chosen for embeddings because:
- Self-hostable (no data leaves our infrastructure)
- 1024 dimensions (good quality/size tradeoff)
- Multi-lingual support (enterprise need)
- Apache 2.0 license

---

## 8. Backend Framework

### 8.1 Decision: Python + FastAPI

| Criteria | FastAPI | Flask | Django | Node.js (Express) | Go (Gin) |
|----------|---------|-------|--------|-------------------|----------|
| **Async Support** | Native (asyncio) | Limited | Partial (3.0+) | Native | Native |
| **AI/ML Ecosystem** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| **Type Safety** | Pydantic | Limited | Django ORM | TypeScript | Strong typing |
| **Performance** | Good (ASGI) | Moderate | Moderate | Good | Excellent |
| **Development Speed** | Very Fast | Fast | Fast | Fast | Moderate |
| **Ecosystem Maturity** | High | Very High | Very High | Very High | High |
| **API Documentation** | Auto (OpenAPI) | Manual | Manual | Swagger | Swagger |

**Rationale**: Python is non-negotiable for an AI-native product — the LLM ecosystem (LangChain, LangGraph, HuggingFace, vLLM, PyTorch, etc.) is Python-native. FastAPI provides the best balance of development speed, async performance, and type safety. Pydantic models ensure that API contracts are well-defined and validated — critical for an AI product where outputs must be predictable.

**Alternatives Considered**:
- **Go**: Better raw performance, but the AI/ML ecosystem gap is too large. Would need to build or wrap every AI component.
- **Node.js/TypeScript**: Better for real-time applications, but Python dominance in AI makes this the wrong choice.

---

## 9. Frontend Technology

### 9.1 Decision: React 19 + Next.js 15

| Criteria | React + Next.js | Vue + Nuxt | SvelteKit | Remix |
|----------|----------------|------------|-----------|-------|
| **SSR/SSG** | Excellent (RSC) | Good | Good | Excellent |
| **Streaming** | Native (RSC) | Limited | Limited | Native |
| **TypeScript** | First-class | First-class | First-class | First-class |
| **Ecosystem** | Largest | Large | Growing | Growing |
| **Component UI** | shadcn/ui (excellent) | Headless UI | Skeleton | N/A |
| **Developer Experience** | Excellent | Good | Excellent | Good |
| **Real-time/SSE** | Good | Good | Good | Good |

**Rationale**: Next.js 15 with React Server Components provides the best architecture for a chat + analytics UI. Streaming enables real-time SQL generation display (token-by-token). shadcn/ui provides well-designed, accessible, customizable components.

---

## 10. Infrastructure

### 10.1 Deployment Architecture (MVP)

```
┌──────────────────────────────────┐
│        Kubernetes (EKS)          │
│                                  │
│  ┌──────────┐  ┌──────────────┐  │
│  │ Web App  │  │ API Server   │  │
│  │ (Next.js)│  │ (FastAPI)    │  │
│  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────────┐  │
│  │ Qdrant   │  │ PostgreSQL   │  │
│  │ (stateful)│  │ (stateful)   │  │
│  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────────┐  │
│  │ Redis    │  │ Inference    │  │
│  │ (cache)  │  │ (GPU node)   │  │
│  └──────────┘  └──────────────┘  │
└──────────────────────────────────┘
```

### 10.2 AMD GPU Node Configuration

| Component | Specification |
|-----------|--------------|
| **GPU** | 4-8x AMD Instinct MI300X (192 GB HBM3 each) |
| **CPU** | AMD EPYC 9654 (96 cores) |
| **RAM** | 1.5 TB DDR5 |
| **Storage** | 4x NVMe SSD (7 TB total) |
| **Network** | 2x 100 Gbps NIC |
| **Software** | ROCm 6.3+, Docker, Kubernetes node |
| **Provider** | AWS EC2 (coming), Azure (coming), on-prem option |

### 10.3 Infrastructure as Code

**Decision**: Terraform + Helm

| Component | Tool | Rationale |
|-----------|------|-----------|
| **Cloud Resources** | Terraform | Cloud-agnostic, state management, module ecosystem |
| **Kubernetes Apps** | Helm | Package management, versioning, templating |
| **CI/CD Pipeline** | GitHub Actions | Tight integration, matrix builds, OIDC auth |
| **Secret Management** | HashiCorp Vault | Enterprise-grade, dynamic secrets, audit logging |

---

## 11. Security & Compliance

### 11.1 Authentication & Authorization

**Decision**: Auth0 (managed) → Keycloak (self-hosted for enterprise)

| Feature | MVP | V1 | Enterprise |
|---------|-----|-----|------------|
| **Auth Provider** | Auth0 | Auth0 | Keycloak / Custom SAML |
| **SSO** | Google, GitHub | + Microsoft, Okta | All (SAML 2.0, OIDC) |
| **RBAC** | Basic (admin/user) | + Viewer, Analyst | Custom roles, SCIM |
| **Column-Level Security** | No | Yes (via schema scoping) | Yes (dynamic masking) |
| **API Keys** | Static | Rotatable | Automatic rotation |
| **Audit Logs** | Basic | Structured | Immutable + export |

### 11.2 Guardrail Stack Implementation

| Layer | Implementation | Status |
|-------|---------------|--------|
| Intent Classification | Qwen2.5-7B classifier + regex patterns | MVP |
| Input Sanitization | Regex whitelist + homoglyph detection | MVP |
| RBAC Schema Scoping | Dynamic DDL generation per role | MVP |
| Query Cost Ceiling | Token estimation + complexity scoring | MVP |
| SQL Syntax Validation | sqlparse + `EXPLAIN` dry-run | MVP |
| Read-Only Execution | Database user with `SELECT ONLY` + transaction isolation | MVP |
| Audit Logging | Structured JSON logs → Loki/Grafana | MVP |

---

## 12. Monitoring & Observability

### 12.1 Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Metrics** | Prometheus + Grafana | System and business metrics |
| **Logging** | Loki | Centralized log aggregation |
| **Tracing** | Tempo (OpenTelemetry) | Distributed tracing across agents |
| **Agent Observability** | LangSmith | Agent decision tracing, token usage |
| **Alerting** | Grafana OnCall / PagerDuty | Incident response |
| **Uptime** | Better Uptime / Checkly | External monitoring |
| **APM** | Grafana Faro (frontend) | Client-side performance |

### 12.2 Key Metrics to Track

| Category | Metric | Target | Alert Threshold |
|----------|--------|--------|-----------------|
| **Business** | Queries per day | 10K+ (V1) | <100 (low usage) |
| **Business** | Execution accuracy | >85% | <70% |
| **Business** | User satisfaction | >90% | <80% |
| **Engineering** | p95 latency | <3s | >5s |
| **Engineering** | Uptime | 99.9% | <99.5% |
| **Engineering** | Error rate | <1% | >3% |
| **AI** | SQL syntax validity | >95% | <90% |
| **AI** | Repair success rate | >50% | <30% |
| **AI** | Router accuracy | >95% | <90% |
| **Cost** | Inference cost/query | <$0.01 avg | >$0.05 |
| **Cost** | GPU utilization | >70% | <40% |

---

## 13. CI/CD & Development Workflow

### 13.1 Pipeline Stages

```
┌─────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌─────────┐
│ Lint    │→│ Type     │→│ Test    │→│ Build  │→│ Deploy  │
│ (ruff)  │  │ (mypy)   │  │ (pytest)│  │ (Docker)│  │ (Helm)  │
└─────────┘  └──────────┘  └─────────┘  └────────┘  └─────────┘
```

### 13.2 Quality Gates

| Gate | Tool | Failure Criteria |
|------|------|------------------|
| Linting | Ruff | Any error-level finding |
| Type Checking | mypy | Any type error (strict mode) |
| Unit Tests | pytest + pytest-asyncio | <90% coverage on core modules |
| Integration | pytest + testcontainers | Any failure in NL2SQL pipeline test |
| Benchmark | pytest-benchmark | >5% regression in latency |
| Security | TruffleHog + Bandit | Any secret leak or high-severity finding |
| Docker Scan | Trivy | Any critical CVE |
| NL2SQL Eval | Custom evaluation suite | >2% regression on held-out test set |

### 13.3 Branch Strategy

```
main ─── staging ─── production
  ▲                        │
  │         release/      │
  │  develop ─────────────┘
  │    │
  └────┘
  feature/
```

---

## 14. Phase 2 Additions

| Technology | Status | Phase | Rationale |
|-----------|--------|-------|-----------|
| Neo4j | **Assess** | Phase 2 | Knowledge graph for multi-hop queries |
| FalkorDB | **Assess** | Phase 2 | Graph-based Text2SQL alternative |
| Unsloth + Axolotl | **Assess** | Phase 2 | Fine-tuning infrastructure |
| MCP Server | **Assess** | Phase 2 | AI agent interoperability (Claude Code, etc.) |
| Kafka / Redpanda | **Assess** | Phase 2 | Event-driven architecture for async processing |
| Kong / Envoy | **Trial** | Phase 2 | API gateway for enterprise multi-tenancy |
| Presto / Trino | **Assess** | Phase 2 | Cross-database federated query (long-term) |
| Cube | **Assess** | Phase 2 | Headless semantic layer for BI tool integration |
| dbt integration | **Assess** | Phase 2 | Semantic model import from existing dbt projects |

---

## 15. Technology Radar

### Adopt (Use in Production)
- Python 3.12, FastAPI, LangGraph, LangSmith
- Qdrant, PostgreSQL 16, Redis
- vLLM (ROCm), SGLang (ROCm)
- Qwen2.5-72B, SQLCoder-7b, BGE-M3
- React 19, Next.js 15, shadcn/ui, Tailwind CSS
- Docker, Kubernetes, Terraform, GitHub Actions
- OpenTelemetry, Grafana, Loki, Tempo
- Auth0, Vault

### Trial (Non-Critical Paths)
- DeepSeek-V3 (SGLang on ROCm)
- RabbitMQ (for async job queue)
- Kong API Gateway

### Assess (Evaluate for Phase 2)
- Neo4j / FalkorDB (knowledge graph)
- Axolotl / Unsloth (fine-tuning)
- MCP Protocol (agent interoperability)
- Presto/Trino (federated query)
- Cube (headless semantic layer)

### Hold (Not Recommended)
- HuggingFace TGI (maintenance mode since Mar 2026)
- TensorRT-LLM (NVIDIA-only, locks us to CUDA)
- Single LLM for all tiers (too expensive)
- Full schema prompting (doesn't scale past 100 tables)
- MongoDB for metadata (ACID without transactions is wrong for this use case)
