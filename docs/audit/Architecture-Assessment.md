# Architecture Assessment

**Score: 72/100 — PARTIALLY VERIFIED**

---

## 1. Overall Architecture

The system follows a microservices-style monolith deployed as separate FastAPI applications within a single Python package:

```
Public API (port 8100)  ←── Frontend (Next.js 15, port 3000)
     │
     └── Knowledge Engine API (port 8200, internal only)
           │
           ├── Schema Store (PostgreSQL)
           ├── Vector Index (Qdrant)
           ├── Knowledge Graph (PostgreSQL)
           ├── Query Pipeline (in-process)
           │     ├── Intent Agent
           │     ├── Context Retrieval
           │     ├── Planner
           │     ├── Generator (NL2SQL)
           │     ├── Guardrail Stack (10 layers)
           │     └── Executor
           ├── Learning Loop (async batch)
           └── Schema Intelligence (sync pipeline)
                 ├── 5 DB Connectors
                 ├── DDL Parser
                 ├── Annotators
                 └── Inference Engine
```

**Verdict: VERIFIED.** The architecture is well-structured with clear separation of concerns.

## 2. Layer Separation

| Layer | Assessment | Evidence |
|-------|-----------|----------|
| API (routes) | ✅ Clean separation | `app/api/v1/` and `ke/api/routes/` — thin controllers |
| Services (business logic) | ✅ Good | `ke/services/` with clear single-responsibility classes |
| Models (Pydantic) | ✅ Excellent | `ke/models/` with proper validation, `from_attributes` |
| Stores (data access) | ✅ Well-designed | `BaseRepository[T]` generic with 10+ concrete repos |
| Migrations | ✅ Proper | Alembic with 6 sequential migrations, RLS policies |

## 3. SOLID Principles

| Principle | Assessment | Evidence |
|-----------|-----------|----------|
| Single Responsibility | ✅ Good | Most classes have clear purpose (IntentAgent, QueryPlanner, etc.) |
| Open/Closed | ⚠️ Partial | `ModelClient` ABC is extensible. `PolicyLayerBase` ABC is extensible. But `BaseRepository` has type issues. |
| Liskov Substitution | ✅ Good | All ModelClient subclasses (HFInferenceClient, OpenAIClient, MockClient) properly implement the interface |
| Interface Segregation | ✅ Good | Small focused interfaces (ModelClient, PolicyLayerBase, BaseAnnotator) |
| Dependency Inversion | ⚠️ Partial | Services import concretions directly (e.g., `QueryPlanner` creates `IntentAgent` internally) |

## 4. Dependency Direction

```
app/ (Public API)  ──→  ke/ (Knowledge Engine)  ──→  ke/stores/  ──→  shared/
```

No circular dependencies detected. The `ke/` package depends on `shared/` for base models, and `app/` depends on `ke/` for the pipeline orchestrator. This is a valid direction.

**Verdict: VERIFIED.** Dependencies flow in the correct direction.

## 5. Key Architectural Findings

### 5.1 CRITICAL: In-Memory State Stores
Sessions (`InMemorySessionService`), alerts (`AlertService` in-memory list), and user feedback processing are all in-memory only. A server restart loses all state. The file-based JSON store for users/tenants was added late and is not suitable for multi-instance deployments.

**Impact:** Any production deployment requires sticky sessions or shared state stores. Learning loop batch processing state is lost on restart.

### 5.2 HIGH: Mock Implementations in Production Path
`InferenceFactory.create()` returns mock clients when API keys are missing. `EmbeddingService` uses deterministic sparse vectors as fallback. The production path (real HF inference, real OpenAI) has never been validated.

**Impact:** The system appears to work in demo mode but has never been tested against real LLM inference or real embedding models.

### 5.3 MEDIUM: Missing Async Boundaries
`IntentAgent.classify()` is synchronous but called within an async pipeline. The `_word_in_query` helper is called synchronously. While Python handles this, it blocks the event loop for the duration of string matching.

### 5.4 MEDIUM: Pipeline Stage Error Handling
The pipeline catches exceptions per-stage and returns `PipelineStatus.FAILED`. However, some stages silently skip on error (schema resolution) while others abort the pipeline (execute). This inconsistency could mask failures.

## 6. Scalability Assessment

| Dimension | Assessment | Evidence |
|-----------|-----------|----------|
| Horizontal scaling | ⚠️ Theoretical | Stateless services (Public API, KE API) can scale. Stores (PG, Qdrant, Redis) are the bottleneck. |
| Multi-tenancy | ✅ Designed | RLS in PG, collection-per-tenant in Qdrant, tenant middleware, tenant-scoped repos |
| Connection pooling | ⚠️ Defaults | `pool_size=5, max_overflow=10` — untuned for production |
| Caching | ❌ Not implemented | Query result cache is TASK-060 (backlog). No Redis caching for frequent queries. |
| Async everywhere | ✅ Good | All I/O operations use async/await throughout the stack |

**Architecture Verdict: 72/100 — Sound architecture with critical gaps in state persistence and production validation.**
