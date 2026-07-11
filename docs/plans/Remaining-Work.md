# Remaining Work — Single Source of Truth

**Generated:** 2026-07-11 | **Sources:** All epics, tasks, release backlog, reviews, ADRs

---

## 1. Must Complete Before Release

Items that block any production release. These address critical security gaps and essential features without which the platform cannot operate safely.

| ID | Title | Source | Reason | Est. | Blocks? | Deps |
|----|-------|--------|--------|------|---------|------|
| EP-005 TASK-036 | Query History store API routes | EP-005 KE API | History visibility required for audit and user feedback | M | Yes | TASK-029 ✅ |
| EP-005 TASK-037 | Feedback store API routes | EP-005 KE API | User feedback collection for Learning Loop | M | Yes | TASK-029 ✅ |
| EP-005 TASK-040 | Audit store API routes | EP-005 KE API | Immutable audit trail required per Security-Spec §11 | M | Yes | TASK-029 ✅ |
| EP-005 TASK-041 | Cache store wrapper | EP-005 KE API | Query result caching required for performance budgets | M | Yes | TASK-029 ✅ |
| EP-005 TASK-038 | Config store API routes | EP-005 KE API | Dynamic tenant configuration | M | No | TASK-029 ✅ |
| EP-005 TASK-039 | Metrics store API routes | EP-005 KE API | Observability data access | M | No | TASK-029 ✅ |
| ~~EP-005 TASK-036–041~~ | ~~KE API remaining routes~~ | ~~EP-005~~ | ✅ **ALREADY DONE** — all routes, stores, and services exist and are wired in main.py | — | — | — |
| RB-011 | JWT auth enforced on routes | Release Backlog / Security | `auto_error=False` permits anonymous access; EP-013 needs this | M | Yes | EP-013 |
| RB-013 | Migration tests | Release Backlog | No DB snapshot test framework for Alembic | M | No | — |
| RB-014 | Helm chart production-ready | Release Backlog | Minimal template, no production config | L | Yes | EP-015 |
| RB-015 | K8s manifests with probes/PDBs/policies | Release Backlog | No liveness/readiness, no PDBs, no network policies | L | Yes | EP-015 |
| RB-016 | Terraform production-ready | Release Backlog | Basic stubs only | L | Yes | EP-015 |
| RB-017 | Container registry config | Release Backlog | CI builds images but no push destination | M | Yes | EP-016 |
| RB-018 | Deployment automation (CD) | Release Backlog | No CD pipeline for auto-deploy | L | Yes | EP-016 |
| RB-019 | Load testing | Release Backlog | `tests/load/` — 4 empty directories | L | Yes | EP-017 |
| RB-020 | Performance baselines | Release Backlog | No benchmark results documented | M | Yes | EP-017 |
| RB-024 | Deployment runbooks | Release Backlog | No deployment documentation | M | No | EP-016 |

---

## 2. Required for Private Beta

Items needed for a functional private beta with limited users. Core query pipeline must work end-to-end.

| ID | Title | Source | Reason | Est. | Deps |
|----|-------|--------|--------|------|------|
| ~~EP-008~~ | ~~Intent & Planning epic~~ | ~~Implementation Plan~~ | ✅ **ALREADY DONE** — intent.py, planner.py, routes/planner.py, models/planning.py all exist with tests | — | — |
| EP-009 | NL2SQL Generation epic (12 tasks) | Implementation Plan | SQL generation with model routing, prerequisite for guardrails | XL | EP-008 ✅ |
| ~~EP-009~~ | ~~NL2SQL Generation epic~~ | ~~Implementation Plan~~ | ✅ **ALREADY DONE** — generator.py, inference.py, router.py, quality_scorer.py all exist with pipechain integration | — | — |
| ~~EP-010~~ | ~~Guardrail Stack epic~~ | ~~Implementation Plan~~ | ✅ **ALREADY DONE** — policy/chain.py, policy/layers.py (10 layers), test_policy.py (~50 tests) | — | — |
| ~~EP-011~~ | ~~Query Executor epic~~ | ~~Implementation Plan~~ | ✅ **ALREADY DONE** — executor.py, routes/executor.py with Pydantic model, security fixes applied | — | — |
| ~~EP-013 TASK-107~~ | ~~Public API query endpoint~~ | ~~EP-013~~ | ✅ **DONE 2026-07-11** — POST /api/v1/query created, proxies to PipelineOrchestrator, JWT protected | S | EP-005 ✅, EP-011 ✅ |
| SPIKE-001 | Context Layer Accuracy research | EP-017 | Research: embedding + retrieval accuracy tuning | M | None |
| SPIKE-002 | Cold-Start Strategy research | EP-017 | Research: handling empty/ sparse schema state | M | None |
| SPIKE-003 | Model Router Accuracy research | EP-017 | Research: model selection accuracy for NL2SQL | M | None |
| EP-012 | Learning Loop epic (7 tasks) | Implementation Plan | Feedback collection, Q&A pairs, schema enrichment | L | EP-005 ✅, EP-011 |

---

## 3. Required for Public Beta

Items needed to expose the platform to external users via the public API and frontend.

| ID | Title | Source | Reason | Est. | Deps |
|----|-------|--------|--------|------|------|
| EP-013 | Public API epic (12 tasks) | Implementation Plan | External REST API with JWT auth, rate limiting, and all endpoints | L | EP-005 ✅, EP-011 |
| ~~EP-013 TASK-113a~~ | ~~Demo-login auth endpoint~~ | ~~EP-013~~ | ✅ **DONE** — `POST /api/v1/auth/demo-login` returns JWT for demo users | S | — |
| ~~EP-013 TASK-113b~~ | ~~Public API tests~~ | ~~EP-013~~ | ✅ **DONE** — 7 tests for auth + query endpoints | M | — |
| EP-014 | Frontend epic (12 tasks) | Implementation Plan | Web UI with chat, schema browser, settings, admin | XL | EP-013 |
| RB-021 | Connection pool tuning | Release Backlog | `pool_size=5, max_overflow=10` are defaults, may not scale | S | EP-011 |

---

## 4. Future Roadmap

Items for GA and post-launch that don't block beta milestones.

| ID | Title | Source | Reason | Est. | Deps |
|----|-------|--------|--------|------|------|
| EP-015 | Multi-Tenant Infra epic (9 tasks) | Implementation Plan | K8s production manifests, Helm, Terraform | M | EP-001 ✅ |
| EP-016 | CI/CD & Observability epic (10 tasks) | Implementation Plan | CD pipeline, monitoring, dashboards, alerting | M | EP-001 ✅, EP-015 |
| RB-022 | README paths | Release Backlog | Already correct — finding was stale | S | None |
| Real BGE-M3 | Replace mock embedding service | Dependency Graph | Mock BGE-M3 → real sentence-transformers | M | EP-006 ✅ |

---

## 5. Technical Debt

Items that degrade code quality, maintainability, or developer experience but don't block milestones.

| ID | Title | Source | Reason | Est. |
|----|-------|--------|--------|------|
| TD-01 | 168 pre-existing Ruff E501 errors | Ruff linter | Line-too-long across 20+ files; low risk, cosmetic | L |
| TD-02 | Pre-existing MyPy errors | MyPy | Missing type annotations, generic type args, conditional redefinitions | L |
| TD-03 | `async def generate()` with sync-only body | `inference.py:MockClient` | Acceptable for mock — no actual `await` needed | S |
| TD-04 | In-memory `AlertService` (no persistence) | `ke/services/alerts.py` | Acceptable for Sprint 0; production needs persistent store | M |
| TD-05 | In-memory `InMemorySessionService` | `ke/services/session.py` | Acceptable for Sprint 0; production needs Redis-backed sessions | M |
| TD-06 | Mock inference client used in production path | `ke/services/inference.py` | Falls through to mock if no real model config found | S |
| TD-07 | EP-005 duplicate EP-001 entry (historical) | Status Dashboard | Fixed by creating EP-018 Core Services | S |
| TD-08 | Dependency Graph task numbering collision (TASK-056–058) | Dependency Graph | Fixed by renumbering to TASK-145–150 | S |
| TD-09 | Missing task files for ~127 tasks | `docs/tasks/` | Only 17 of ~144 task files exist; rest generated from epic tables | L |
| TD-10 | Windows `make install` issue | Makefile | `cd backend && uv sync` fails in Git Bash on Windows | S |

---

## Summary

| Category | Count | Total Est. Effort |
|----------|-------|-------------------|
| 🛑 Must Complete Before Release | 17 items | ~20-30 days |
| 🔷 Required for Private Beta | 4 epics + 3 spikes = ~36 tasks | ~12-16 weeks |
| 🔶 Required for Public Beta | 2 epics + 1 task = ~25 tasks | ~8-12 weeks |
| 🟢 Future Roadmap | 3 items | ~2-4 weeks |
| 🟡 Technical Debt | 10 items | ~2-5 days |

**Critical Path for Private Beta**: EP-008 → EP-009 → EP-010 → EP-011 → EP-013

**Current Blocking Dependencies**: EP-017 (Research Spikes) must complete before or in parallel with EP-008.
