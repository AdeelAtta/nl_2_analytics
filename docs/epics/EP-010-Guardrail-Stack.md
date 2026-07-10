# EP-010: Policy Enforcement Stack

Epic ID: **EP-010** | Priority: **P0** | Dependencies: **EP-002** | Complexity: **Large** | Agent: **Query Pipeline Agent**

---

Implement the 10-layer fail-closed policy enforcement stack that ensures security, safety, and correctness before SQL execution. L2-L10 are fully deterministic (no LLM). Modeled after ASK-TARA's production system (90K queries, zero incidents).

## Goals
- L1 Intent Classification (LLM-assisted, skip on timeout → default "unknown")
- L2 SQL Sanitization (SQL injection prevention via sqlglot AST)
- L3 RBAC Schema Scoping (authorized tables only)
- L4 Cost Ceiling (prevent runaway queries)
- L5 SQL Validation (syntax + semantic correctness)
- L6 Read-Only Enforcement (no DDL/DML/DCL)
- L7 Audit Logging (every query logged)
- L8 Data Classification (PII detection, cross-tenant check, exfiltration prevention)
- L9 Advanced Validation (SQL allowlist/denylist, dangerous function detection, resource quotas)
- L10 Anomaly Detection (per-tenant query baseline comparison)

## Out of Scope
- Authentication (EP-013)
- Tenant context extraction (EP-005)

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-079 | Implement policy enforcement framework (chain-of-responsibility) | P0 | EP-002 | L |
| TASK-080 | Implement Intent Classification Layer (L1) | P0 | TASK-079 | M |
| TASK-081 | Implement SQL Sanitization Layer (L2) | P0 | TASK-079 | M |
| TASK-082 | Implement RBAC Schema Scoping Layer (L3) | P0 | TASK-079, EP-002 | L |
| TASK-083 | Implement Cost Ceiling Layer (L4) | P0 | TASK-079 | M |
| TASK-084 | Implement SQL Validation Layer (L5, sqlglot-based) | P0 | TASK-079 | L |
| TASK-085 | Implement Read-Only Enforcement Layer (L6) | P0 | TASK-079 | S |
| TASK-086 | Implement Audit Logging Layer (L7) | P0 | TASK-079 | M |
| TASK-087 | Implement Data Classification Layer (L8) | P0 | TASK-079 | L |
| TASK-088 | Implement Advanced Validation Layer (L9) | P0 | TASK-079 | M |
| TASK-089 | Implement Anomaly Detection Layer (L10) | P1 | TASK-079 | L |
| TASK-090 | Write unit and integration tests | P0 | TASK-079 | XL |

## Acceptance Criteria
- All 10 layers pass valid queries without false positives (>95%)
- L2-L10 are fully deterministic (zero LLM calls)
- SQL injection attempts blocked with 100% detection
- RBAC blocks unauthorized table access with 100% accuracy
- Cost ceiling blocks queries estimated > 10M rows
- Read-only enforcement blocks all INSERT/UPDATE/DELETE/DDL
- PII detection flags known PII column patterns with > 95% accuracy
- SQL allowlist/denylist enforced with zero LLM dependency
- Anomaly detection flags queries > 2σ from per-tenant baseline
- Each layer adds < 50ms overhead (P95) except L1 (LLM, < 100ms)
- Audit log includes: tenant_id, user_id, query_hash, SQL, decision, timestamp, layer_results

## Definition of Done
- All 10 layers implemented, unit tested, integration tested
- Security penetration test: 0 bypasses
- Performance budget: total policy enforcement overhead < 450ms P95
