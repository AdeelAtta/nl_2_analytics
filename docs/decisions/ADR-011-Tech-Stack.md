# ADR-011: Technology Stack Selection

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-011 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Phase 1 research evaluated multiple technology candidates for each layer. This ADR finalizes the technology stack for implementation based on the Technology-Recommendations.md analysis.

## Decision

We will use the following technology stack:

| Layer | Decision | Alternatives Considered |
|-------|----------|----------------------|
| **Python runtime** | Python 3.12 (uv package manager) | Poetry, pipenv — uv is fastest |
| **API framework** | FastAPI 0.115+ | Flask, Litestar — FastAPI has best async + OpenAPI support |
| **Agent orchestration** | LangGraph (latest) | CrewAI, AutoGen — LangGraph best for DAG+cycle graphs |
| **ORM** | SQLAlchemy 2.0+ (async) | SQLModel, Django ORM — SQLAlchemy most mature async PG support |
| **Vector store** | Qdrant 1.12+ (self-hosted) | Pinecone, Weaviate, Milvus — best filtered search, self-hosted |
| **Embeddings** | BGE-M3 (sentence-transformers) | OpenAI ada-002, e5-mistral — open source, 1024-dim, multi-lingual |
| **SQL parser** | sqlglot (latest) | sqlparse, mo-sql-parsing — sqlglot best AST + dialect support |
| **Frontend** | React 19 + Next.js 15 | Remix, SvelteKit — Next.js most mature ecosystem |
| **UI kit** | shadcn/ui + Tailwind CSS | MUI, Chakra — shadcn best DX, no runtime CSS-in-JS |
| **State management** | Zustand | Redux, Jotai — Zustand simplest, good TS support |
| **Frontend API client** | openapi-typescript | tRPC, graphql-codegen — auto-generated from OpenAPI spec |
| **Container runtime** | Docker 27+ | Podman — Docker industry standard |
| **Orchestration** | Kubernetes 1.30+ | Nomad, Docker Swarm — K8s most portable |
| **IaC** | Terraform 1.9+ (OpenTofu compatible) | Pulumi, CDK — Terraform cloud-agnostic standard |
| **CI/CD** | GitHub Actions | GitLab CI, CircleCI — co-located with code |

## Rationale

- **Python 3.12** provides pattern matching, improved error messages, and is the minimum for LangGraph ecosystem
- **uv** is 10-100x faster than pip/poetry for dependency resolution, critical for CI speed
- **FastAPI** is the only Python framework with first-class async + auto OpenAPI generation
- **LangGraph** uniquely supports cyclic graphs needed for repair-reflection loops
- **Qdrant** has best filtered search performance (CRITICAL for multi-tenant) and is Apache 2.0 licensed
- **shadcn/ui** provides copy-paste components without runtime CSS-in-JS overhead

## Consequences

### Positive
- Consistent, well-supported technology stack across all layers
- All components are open source (no vendor lock-in, except GitHub Actions)
- Fast development iteration with FastAPI's auto-reload and OpenAPI generation
- Qdrant self-hosted enables all 5 deployment modes including air-gapped
- GPU vendor independence: inference abstraction layer uses vLLM/SGLang with AMD ROCm + CUDA support

### Negative
- Python ecosystem complexity (venv management, slow tests without careful design)
- LangGraph is relatively new (breaking changes possible)
- Qdrant self-hosted adds operational overhead vs managed Pinecone
- shadcn/ui requires manual component updates vs MUI's automatic upgrade path

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Python dependency conflict from deep dependency tree | Medium | Medium | uv lockfile; dependabot for automated updates; CI dependency vulnerability scanning |
| LangGraph breaking changes during development cycle | Medium | High | Pin LangGraph version; API surface contract tests; deliberate upgrade process |
| Next.js major version migration disrupts frontend development | Low | Medium | Long-term support (LTS) pinning; incremental upgrade per major version; feature-flag based rollout |
| vLLM/SGLang AMD ROCm compatibility regression | Medium | High | Version pinning; pre-deployment model health check; cloud inference fallback |
| SQLAlchemy async ORM complexity slows backend development | Medium | Medium | Raw SQL for complex queries; ORM for standard CRUD only; comprehensive async test patterns |

## Trade-offs

- **FastAPI vs Litestar/Flask**: FastAPI chosen for best async + OpenAPI support in Python ecosystem. Litestar offers similar performance with stricter typing but smaller community. Flask is simpler but lacks native async and auto-OpenAPI. FastAPI provides the best balance of features, ecosystem, and documentation
- **SQLAlchemy async vs raw SQL**: SQLAlchemy 2.0 async provides type-safe query building and migration tooling (Alembic) at the cost of ORM complexity. Raw SQL offers maximum performance and simplicity for complex analytical queries. Decision: ORM for CRUD, raw SQL for analytical/complex queries
- **React 19 + Next.js 15 vs Remix/SvelteKit**: Next.js provides the most mature React ecosystem with server components, streaming, and broad hosting support. Remix offers simpler data loading. SvelteKit better performance but smaller ecosystem. Next.js chosen for ecosystem maturity and team hiring pool
- **shadcn/ui vs MUI**: shadcn/ui provides Tailwind-first components with copy-paste model (no npm dependency for components) but requires manual updates. MUI provides automatic upgrades with heavier bundle size and runtime CSS-in-JS. shadcn chosen for bundle size and design flexibility

## Related ADRs

- ADR-001: Knowledge Engine as Architectural Core (FastAPI services implement KE API)
- ADR-007: LangGraph for Agent Orchestration (Python + LangGraph ecosystem)
- ADR-013: Frontend Technology Stack (React 19, Next.js, Zustand, shadcn/ui) — formerly part of this ADR, now separated
- ADR-014: CI/CD and Infrastructure Stack (Docker, K8s, Terraform, GitHub Actions) — formerly part of this ADR, now separated

## References

- [Technology-Recommendations.md](../Technology-Recommendations.md)
- [Architecture-Review.md](../Architecture-Review.md) §2 (Technology Stack section)
- [Engineering-Standards.md](../specifications/Engineering-Standards.md) §2 (Technology Standards)
