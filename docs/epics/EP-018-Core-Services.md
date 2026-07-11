# EP-018: Core Services — Quality, PII, Alerts

| Metadata | Value |
|----------|-------|
| **Epic ID** | EP-018 |
| **Priority** | P1 |
| **Dependencies** | EP-001 |
| **Complexity** | S |
| **Agent Owner** | Knowledge Engine Agent |
| **Status** | ✅ Complete |

---

Implement cross-cutting core services that support multiple downstream epics: schema quality scoring, PII column detection, and centralized alerting.

## Goals
- Schema quality scoring service (coverage, completeness, consistency, freshness)
- PII column classification via regex patterns
- Centralized pub-sub alert service with category/severity/handler model
- All services accessible from `ke/services/` without external dependencies

## Out of Scope
- Persistent alert store (in-memory only for Sprint 0)
- Data-scanning PII detection (name-based only)
- Quality dashboard UI

## Tasks

| ID | Name | P | Deps | Est | Status |
|----|------|---|------|-----|--------|
| TASK-056 | Schema quality score service | P1 | EP-001 | S | ✅ done |
| TASK-057 | PII column detection service | P1 | EP-001 | S | ✅ done |
| TASK-058 | Centralized alert service | P1 | EP-001 | S | ✅ done |

## Status: ✅ Complete (3/3)

## Acceptance Criteria
- QualityScoreService computes overall score + 4 dimensions from TableRepository + ColumnRepository
- PIIDetector classifies columns across 15 categories with sensitivity levels
- AlertService supports 5 categories, 4 severity levels, handler registration, and filtering
- All services have passing tests and pass ruff/mypy

## Deliverables Created
- `ke/services/quality.py` — QualityScoreService (15 tests)
- `ke/services/pii.py` — PIIDetector with 15 PII pattern categories (18 tests)
- `ke/services/alerts.py` — AlertService with 5 alert categories (16 tests)
- 49 total tests, all pass, ruff clean
