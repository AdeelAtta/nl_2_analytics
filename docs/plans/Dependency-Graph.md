# Dependency Graph — Enterprise Data Intelligence Platform

**Generated**: 2026-07-10 | **Architecture**: v1.0 (frozen) | **Total Epics**: 17 | **Total Tasks**: ~144

---

## 1. Epic-Level Dependency Graph

```
                    ┌──────────────────────────────────────────────────────────────┐
                    │                     EP-001: Dev Environment                   │
                    │           (8 tasks, P0/P1, Infra Agent, Est: M)              │
                    └──────────┬──────────┬──────────┬──────────┬──────────────────┘
                               │          │          │          │
                 ┌─────────────┘          │          │          └─────────────┐
                 ▼                        ▼          ▼                        ▼
        ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
        │  EP-015: Infra   │    │  EP-016: CI/CD   │    │  EP-017: Spikes  │    │  EP-002: Schema  │
        │  (9 tasks, P0)   │    │  (10 tasks, P0)  │    │  (3 spikes, P0)  │    │  (7 tasks, P0)   │
        │  Infra Agent     │    │  Infra Agent     │    │  Research Agent  │    │  KE Agent        │
        │  Est: M          │    │  Est: M          │    │  Est: M          │    │  Est: L          │
        └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
                 │                       │                       │                       │
                 │                       │                       │  (deps: TASK-008)    │
                 │                       │                       │                       │
                 │                       │                       ├───────────────────────┤
                 │                       │                       │                       │
                 │                       │                       ▼                       ▼
                 │                       │              ┌──────────────────┐    ┌──────────────────┐
                 │                       │              │  EP-003: Vector  │    │  EP-004: Graph   │
                 │                       │              │  (7 tasks, P0)   │    │  (6 tasks, P1)   │
                 │                       │              │  KE Agent        │    │  KE Agent        │
                 │                       │              │  Est: M          │    │  Est: M          │
                 │                       │              └────────┬─────────┘    └────────┬─────────┘
                 │                       │                       │                       │
                 │                       │                       │                       │
                 │                       │                       ├───────────────────────┤
                 │                       │                       │                       │
                 │                       │                       ▼                       ▼
                 │                       │              ┌──────────────────┐    ┌──────────────────┐
                 │                       │              │  EP-005: KE API  │    │  EP-006: Schema  │
                 │                       │              │ (14 tasks, P0)   │    │ (13 tasks, P0)   │
                 │                       │              │  KE Agent        │    │  Schema Intel    │
                 │                       │              │  Est: XL         │    │  Est: XL         │
                 │                       │              └────────┬─────────┘    └────────┬─────────┘
                 │                       │                       │                       │
                 │                       │                       │                       │
                 │                       │                       ▼                       │
                 │                       │              ┌──────────────────┐            │
                 │                       │              │  EP-007: Context │◄───────────┘
                 │                       │              │  (6 tasks, P0)   │   (needs SPIKE-001/002)
                 │                       │              │  Query Pipeline  │
                 │                       │              │  Est: M          │
                 │                       │              └────────┬─────────┘
                 │                       │                       │
                 │                       │                       ▼
                 │                       │              ┌──────────────────┐
                 │                       │              │  EP-008: Intent  │
                 │                       │              │  (5 tasks, P0)   │
                 │                       │              │  Query Pipeline  │
                 │                       │              │  Est: L          │
                 │                       │              └────────┬─────────┘
                 │                       │                       │
                 │                       │                       ▼
                 │                       │              ┌──────────────────┐
                 │                       │              │  EP-009: NL2SQL  │
                 │                       │              │ (12 tasks, P0)   │
                 │                       │              │  Query Pipeline  │
                 │                       │              │  Est: XL         │
                 │                       │              └────────┬─────────┘
                 │                       │                       │
                 │                       │                       ▼
                 │                       │              ┌──────────────────┐
                 │                       │              │  EP-010: Guards  │
                 │                       │              │  (9 tasks, P0)   │
                 │                       │              │  Query Pipeline  │
                 │                       │              │  Est: L          │
                 │                       │              └────────┬─────────┘
                 │                       │                       │
                 │                       │                       ▼
                 │                       │              ┌──────────────────┐
                 │                       │              │  EP-011: Executor│
                 │                       │              │  (7 tasks, P0)   │
                 │                       │              │  Query Pipeline  │
                 │                       │              │  Est: M          │
                 │                       │              └────────┬─────────┘
                 │                       │                       │
                 │                       │                       ├─────────────────────┐
                 │                       │                       │                     │
                 │                       │                       ▼                     ▼
                 │                       │              ┌──────────────────┐    ┌──────────────────┐
                 │                       │              │  EP-012: Learn   │    │  EP-013: Pub API │
                 │                       │              │  (7 tasks, P1)   │    │ (12 tasks, P0)   │
                 │                       │              │  KE Agent        │    │  API Agent       │
                 │                       │              │  Est: L          │    │  Est: L          │
                 │                       │              └──────────────────┘    └────────┬─────────┘
                 │                       │                                               │
                 │                       │                                               ▼
                 │                       │                                      ┌──────────────────┐
                 │                       │                                      │  EP-014: Frontend│
                 │                       │                                      │ (12 tasks, P1)   │
                 │                       │                                      │  Frontend Agent  │
                 │                       │                                      │  Est: XL         │
                 │                       │                                      └──────────────────┘
                 ▼                       ▼
        ┌───────────────────────────────────────────────────────┐
        │        EP-015 + EP-016: Infra Track                   │
        │  (parallel to KE/Pipeline/API/Frontend tracks)        │
        │  TASK-126 through TASK-144 (19 total)                │
        └───────────────────────────────────────────────────────┘
```

---

## 2. Task-Level Dependency Table

### EP-001: Dev Environment (Infrastructure Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-001 | Monorepo structure | None | done | TASK-002–008, TASK-029, TASK-102, TASK-114, TASK-126, TASK-135 |
| TASK-002 | Python tooling | TASK-001 | done | TASK-006, TASK-008 |
| TASK-003 | Node.js/Next.js tooling | TASK-001 | done | — |
| TASK-004 | Docker Compose | TASK-001 | done | — |
| TASK-005 | Makefile | TASK-001 | done | — |
| TASK-006 | Pre-commit hooks | TASK-002 | done | — |
| TASK-007 | README | TASK-001 | done | — |
| **TASK-008** | **Shared models** | **TASK-002** | **done** | **TASK-009, TASK-043** |

### EP-002: Schema Store (Knowledge Engine Agent) — **UNBLOCKED**

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| **TASK-009** | **Data models** | **TASK-008** | **done** | TASK-010 |
| TASK-010 | Alembic migration | TASK-009 | ready | TASK-011 |
| TASK-010 | Alembic migration | TASK-009 | backlog | TASK-011 |
| TASK-011 | CRUD repository | TASK-010 | backlog | TASK-012, TASK-013, TASK-014, TASK-015 |
| TASK-012 | Schema versioning | TASK-011 | backlog | — |
| TASK-013 | RLS policies | TASK-011 | backlog | — |
| TASK-014 | Unit tests | TASK-011 | backlog | — |
| TASK-015 | Integration tests | TASK-011 | backlog | — |

### EP-003: Vector Index (Knowledge Engine Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-016 | Qdrant client & pool | TASK-001 | backlog | TASK-018, TASK-019 |
| TASK-017 | BGE-M3 embedding service | TASK-001 | backlog | — |
| TASK-018 | Vector point schemas | TASK-016 | backlog | — |
| TASK-019 | Qdrant CRUD repository | TASK-016 | backlog | TASK-020, TASK-021, TASK-022 |
| TASK-020 | Per-tenant collections | TASK-019 | backlog | — |
| TASK-021 | Hybrid search | TASK-019 | backlog | — |
| TASK-022 | Tests | TASK-019 | backlog | — |

### EP-004: Knowledge Graph (Knowledge Engine Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-023 | Graph data models | TASK-009 | backlog | TASK-024 |
| TASK-024 | Node CRUD repository | TASK-023 | backlog | TASK-026, TASK-027, TASK-028 |
| TASK-025 | Edge CRUD repository | TASK-023 | backlog | — |
| TASK-026 | Recursive CTE traversal | TASK-024 | backlog | — |
| TASK-027 | Ontology import/export | TASK-024 | backlog | — |
| TASK-028 | Tests | TASK-024 | backlog | — |

### EP-005: KE API Layer (Knowledge Engine Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-029 | Scaffold KE API | TASK-001 | backlog | TASK-030–042 |
| TASK-030 | Unified response format | TASK-029 | backlog | — |
| TASK-031 | Tenant middleware | TASK-029 | backlog | — |
| TASK-032 | Internal auth | TASK-029 | backlog | — |
| TASK-033 | Schema Store routes | TASK-029, EP-002 | backlog | — |
| TASK-034 | Vector Index routes | TASK-029, EP-003 | backlog | — |
| TASK-035 | Graph Store routes | TASK-029, EP-004 | backlog | — |
| TASK-036 | Query History routes | TASK-029 | backlog | — |
| TASK-037 | Feedback routes | TASK-029 | backlog | — |
| TASK-038 | Config routes | TASK-029 | backlog | — |
| TASK-039 | Metrics routes | TASK-029 | backlog | — |
| TASK-040 | Audit routes | TASK-029 | backlog | — |
| TASK-041 | Cache wrapper | TASK-029 | backlog | — |
| TASK-042 | Integration tests | TASK-033 | backlog | — |

### EP-006: Schema Intelligence (Schema Intelligence Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| **TASK-043** | **DB connector interface** | **TASK-008** | **backlog** | TASK-044–048 |
| TASK-044 | PostgreSQL connector | TASK-043 | backlog | — |
| TASK-045 | MySQL connector | TASK-043 | backlog | — |
| TASK-046 | Snowflake connector | TASK-043 | backlog | — |
| TASK-047 | BigQuery connector | TASK-043 | backlog | — |
| TASK-048 | DuckDB connector | TASK-043 | backlog | — |
| TASK-049 | DDL parser | TASK-043 | backlog | TASK-050, TASK-051 |
| TASK-050 | LLM description annotator | TASK-049 | backlog | TASK-052, TASK-053, TASK-055 |
| TASK-051 | Relationship inference | TASK-049 | backlog | — |
| TASK-052 | Incremental sync orchestrator | TASK-050 | backlog | TASK-054 |
| TASK-053 | Schema-to-embedding pipeline | TASK-050, EP-003 | backlog | — |
| TASK-054 | Metadata-to-KE sync | TASK-052, EP-005 | backlog | — |
| TASK-055 | Tests | TASK-050 | backlog | — |

### EP-007: Context Retrieval (Query Pipeline Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-056 | Query embedding service | EP-003 | backlog | TASK-057 |
| TASK-057 | Hybrid retriever | TASK-056, EP-005 | backlog | TASK-058, TASK-060, TASK-061 |
| TASK-058 | Context ranking & dedup | TASK-057 | backlog | TASK-059 |
| TASK-059 | Context window trimmer | TASK-058 | backlog | — |
| TASK-060 | Query result cache | TASK-057 | backlog | — |
| TASK-061 | Tests | TASK-057 | backlog | — |

### EP-008: Intent & Planning (Query Pipeline Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-062 | Intent Agent | EP-007 | backlog | TASK-063, TASK-065, TASK-066 |
| TASK-063 | Query plan generation | TASK-062 | backlog | TASK-064 |
| TASK-064 | Plan validation | TASK-063 | backlog | — |
| TASK-065 | Model router | TASK-062 | backlog | — |
| TASK-066 | Tests | TASK-062 | backlog | — |

### EP-009: NL2SQL Generation (Query Pipeline Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-067 | LangGraph orchestration | EP-008 | backlog | TASK-068–071, TASK-076, TASK-077 |
| TASK-068 | SQLCoder-7b-2 wrapper | TASK-067 | backlog | TASK-072 |
| TASK-069 | Qwen2.5-72B wrapper | TASK-067 | backlog | — |
| TASK-070 | DeepSeek-V3 wrapper | TASK-067 | backlog | — |
| TASK-071 | GPT-4o fallback | TASK-067 | backlog | — |
| TASK-072 | Multi-candidate generator | TASK-068 | backlog | TASK-073, TASK-074, TASK-078 |
| TASK-073 | Candidate selector | TASK-072 | backlog | — |
| TASK-074 | Reflection Agent | TASK-072 | backlog | TASK-075 |
| TASK-075 | Repair Agent | TASK-074 | backlog | — |
| TASK-076 | Inference abstraction | TASK-067 | backlog | — |
| TASK-077 | Cost tracking | TASK-067 | backlog | — |
| TASK-078 | Tests | TASK-072 | backlog | — |

### EP-010: Guardrail Stack (Query Pipeline Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-079 | Policy framework | EP-002 | backlog | TASK-080–090 |
| TASK-080 | L1: Intent Classification | TASK-079 | backlog | — |
| TASK-081 | L2: SQL Sanitization | TASK-079 | backlog | — |
| TASK-082 | L3: RBAC Schema Scoping | TASK-079, EP-002 | backlog | — |
| TASK-083 | L4: Cost Ceiling | TASK-079 | backlog | — |
| TASK-084 | L5: SQL Validation | TASK-079 | backlog | — |
| TASK-085 | L6: Read-Only Enforcement | TASK-079 | backlog | — |
| TASK-086 | L7: Audit Logging | TASK-079 | backlog | — |
| TASK-087 | L8: Data Classification | TASK-079 | backlog | — |
| TASK-088 | L9: Advanced Validation | TASK-079 | backlog | — |
| TASK-089 | L10: Anomaly Detection | TASK-079 | backlog | — |
| TASK-090 | Tests | TASK-079 | backlog | — |

### EP-011: Query Executor (Query Pipeline Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-091 | Connection pool manager | EP-010 | backlog | TASK-092 |
| TASK-092 | SQL executor with timeout | TASK-091 | backlog | TASK-093, TASK-094, TASK-095, TASK-096 |
| TASK-093 | Result formatter | TASK-092 | backlog | — |
| TASK-094 | Error handler | TASK-092 | backlog | — |
| TASK-095 | Dry-run mode | TASK-092 | backlog | — |
| TASK-096 | Result pagination | TASK-092 | backlog | — |
| TASK-097 | Tests | TASK-092 | backlog | — |

### EP-012: Learning Loop (Knowledge Engine Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-098 | Feedback collector | EP-005 | backlog | TASK-099–104 |
| TASK-099 | Feedback validator/dedup | TASK-098 | backlog | — |
| TASK-100 | Q&A pair builder | TASK-098 | backlog | — |
| TASK-101 | Schema enricher | TASK-098 | backlog | — |
| TASK-102 | Pattern miner | TASK-098 | backlog | — |
| TASK-103 | Batch scheduler | TASK-098 | backlog | — |
| TASK-104 | Tests | TASK-098 | backlog | — |

### EP-013: Public API (API Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-105 | Scaffold Public API | EP-001 | backlog | TASK-106–114 |
| TASK-106 | JWT auth middleware | TASK-105 | backlog | TASK-107 |
| TASK-107 | API key auth | TASK-106 | backlog | — |
| TASK-108 | Rate limiting | TASK-105 | backlog | — |
| TASK-109 | CORS config | TASK-105 | backlog | — |
| TASK-110 | Query endpoint | TASK-105, EP-011 | backlog | — |
| TASK-111 | Schema exploration | TASK-105, EP-005 | backlog | — |
| TASK-112 | History endpoints | TASK-105 | backlog | — |
| TASK-113 | Feedback endpoints | TASK-105 | backlog | — |
| TASK-114 | Admin endpoints | TASK-105 | backlog | — |
| TASK-115 | Request logging | TASK-105 | backlog | — |
| TASK-116 | Tests | TASK-110 | backlog | — |

### EP-014: Frontend (Frontend Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-117 | Scaffold Next.js 15 | EP-001 | backlog | TASK-118–128 |
| TASK-118 | shadcn/ui + Tailwind | TASK-117 | backlog | TASK-119 |
| TASK-119 | Design system | TASK-118 | backlog | — |
| TASK-120 | API client library | TASK-117, EP-013 | backlog | TASK-121 |
| TASK-121 | Zustand state stores | TASK-117 | backlog | — |
| TASK-122 | Chat interface | TASK-120 | backlog | — |
| TASK-123 | Schema browser | TASK-120 | backlog | — |
| TASK-124 | Query history sidebar | TASK-120 | backlog | — |
| TASK-125 | Settings pages | TASK-120 | backlog | — |
| TASK-126 | Admin dashboard | TASK-120 | backlog | — |
| TASK-127 | Auth UI | TASK-120 | backlog | — |
| TASK-128 | Tests | TASK-122 | backlog | — |

### EP-015: Multi-Tenant Infra (Infrastructure Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-129 | Dockerfiles for all services | EP-001 | backlog | TASK-130, TASK-132 |
| TASK-130 | K8s manifests (dev) | TASK-129 | backlog | TASK-131, TASK-133–137 |
| TASK-131 | Helm charts | TASK-130 | backlog | — |
| TASK-132 | Terraform modules | TASK-129 | backlog | — |
| TASK-133 | K8s namespaces & network policies | TASK-130 | backlog | — |
| TASK-134 | HPA configurations | TASK-130 | backlog | — |
| TASK-135 | Ingress configuration | TASK-130 | backlog | — |
| TASK-136 | Secret management | TASK-130 | backlog | — |
| TASK-137 | Infrastructure tests | TASK-130 | backlog | — |

### EP-016: CI/CD & Observability (Infrastructure Agent)

| Task | Name | Deps | Status | Blocks |
|------|------|------|--------|--------|
| TASK-138 | CI workflow | EP-001 | backlog | TASK-140 |
| TASK-139 | CD workflow | EP-015 | backlog | — |
| TASK-140 | Docker image registry | TASK-138 | backlog | — |
| TASK-141 | Health check endpoints | EP-001 | backlog | — |
| TASK-142 | Prometheus + Grafana | EP-015 | backlog | TASK-146 |
| TASK-143 | Structured JSON logging | EP-001 | backlog | TASK-144 |
| TASK-144 | Loki log aggregation | TASK-143 | backlog | — |
| TASK-145 | Sentry integration | EP-001 | backlog | — |
| TASK-146 | Grafana dashboards | TASK-142 | backlog | — |
| TASK-147 | Alerting rules | TASK-142 | backlog | — |

### EP-017: Research Spikes (Research Agent)

| Spike | Name | Deps | Status | Unblocks |
|-------|------|------|--------|----------|
| SPIKE-001 | Context Layer Accuracy | None | not started | EP-007 |
| SPIKE-002 | Cold-Start Strategy | None | not started | EP-007 |
| SPIKE-003 | Model Router Accuracy | None | not started | EP-008 |

---

## 3. Critical Path (Longest Dependency Chain)

The longest chain from start to finish:

```
TASK-001 → TASK-002 → TASK-008 → TASK-009 → TASK-010 → TASK-011
  └→ EP-002 done
    └→ EP-003 (parallel, TASK-016 → TASK-019)
      └→ EP-005 (TASK-029 → TASK-033 → TASK-042)
        └→ EP-007 (TASK-056 → TASK-057 → TASK-061)
          └→ EP-008 (TASK-062 → TASK-066)
            └→ EP-009 (TASK-067 → TASK-072 → TASK-078)
              └→ EP-010 (TASK-079 → TASK-090)
                └→ EP-011 (TASK-091 → TASK-097)
                  └→ EP-013 (TASK-105 → TASK-116)
                    └→ EP-014 (TASK-117 → TASK-128)
```

**Critical path length**: ~50 tasks (sequential)

---

## 4. Parallelism Opportunities

### Track A: Infrastructure (Infra Agent)
```
EP-001 (remaining) ──▶ EP-015 ──▶ EP-016
                          ▲
                          └── Can start after EP-001 done
```

### Track B: Knowledge Engine (KE Agent)
```
EP-001 ──▶ EP-002 ──▶ EP-004
               └──▶ EP-003 ──▶ EP-005 ──▶ EP-012
```

### Track C: Schema Intelligence (Schema Intel Agent)
```
EP-001 ──▶ EP-006 (depends on EP-002 + EP-003 but can start TASK-043 after TASK-008)
```

### Track D: Query Pipeline (Pipeline Agent)
```
EP-005 ──▶ EP-007 ──▶ EP-008 ──▶ EP-009 ──▶ EP-010 ──▶ EP-011
```

### Track E: API + Frontend (API + Frontend Agents)
```
EP-005+EP-011 ──▶ EP-013 ──▶ EP-014
```

### Track F: Research (Research Agent)
```
EP-017 (independent, runs in parallel with all tracks)
```

---

## 5. Key Scheduling Constraints

| Constraint | Reason |
|-----------|--------|
| EP-002 and EP-003 must both complete before EP-005 | EP-005 serves routes for both Schema Store and Vector Index |
| EP-002 and EP-003 must both complete before EP-006 | Schema Intelligence writes to both stores |
| EP-005 must complete before EP-007 | Context Retrieval queries KE API |
| EP-007 must complete before EP-008 | Intent Agent uses context from retrieval |
| EP-008 must complete before EP-009 | Query Plan from EP-008 is input to NL2SQL generation |
| EP-009 must complete before EP-010 | Guardrail stack validates generated SQL |
| EP-010 must complete before EP-011 | Executor runs validated SQL only |
| EP-005 and EP-011 must complete before EP-013 | Public API wraps KE API + Query Executor |
| EP-013 must complete before EP-014 | Frontend consumes Public API |
| EP-005 and EP-011 must complete before EP-012 | Learning Loop uses KE API + Query Executor |
| EP-017 must complete before EP-007/EP-008 | Research results may change retrieval/planning design |
| EP-015 and EP-016 are independent of KE/Pipeline tracks | Can run in parallel |

---

## 6. Current Blockers

| Blocker | Location | Blocks | Since |
|---------|----------|--------|-------|
| No git commits | Root | All work unversioned | Sprint 0 |
| Research spikes not started | EP-017 | EP-007 (TASK-056), EP-008 (TASK-065) | Start of Phase 4 |
| Makefile Windows issue | Root | Developer onboarding | Sprint 0 |

---

## 7. Unblocking Priority Order

```
Priority 1 ──▶ Git commit — version all work
Priority 2 ──▶ EP-017 (Research Spikes) — must complete before EP-007/EP-008
Priority 3 ──▶ TASK-009 (EP-002) — Schema Store data models (now unblocked)
Priority 4 ──▶ TASK-016 (EP-003) — Qdrant client (parallel with EP-002)
Priority 5 ──▶ Makefile Windows fix — developer experience
```

## 8. Newly Unblocked Tasks

The following tasks are now **ready** (all dependencies met):

| Task | Epic | Agent | Dependencies |
|------|------|-------|-------------|
| **TASK-010** | EP-002 (Schema Store) | Knowledge Engine | TASK-009 ✅ |
| **TASK-043** | EP-006 (Schema Intelligence) | Schema Intelligence | TASK-008 ✅ |
| TASK-016 | EP-003 (Vector Index) | Knowledge Engine | TASK-001 ✅ |
| TASK-017 | EP-003 (Vector Index) | Knowledge Engine | TASK-001 ✅ |
| TASK-029 | EP-005 (KE API) | Knowledge Engine | TASK-001 ✅ |
| TASK-102 | EP-013 (Public API) | API | EP-001 ✅ |
| TASK-114 | EP-014 (Frontend) | Frontend | EP-001 ✅ |
| TASK-126 | EP-015 (Multi-Tenant Infra) | Infrastructure | EP-001 ✅ |
| TASK-135 | EP-016 (CI/CD) | Infrastructure | EP-001 ✅ |

**Note**: Some tasks above (TASK-029, 102, 114, 126, 135) are structurally ready but their downstream dependencies (EP-002, EP-005, EP-011) limit how far they can proceed independently.
