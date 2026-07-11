# ADR-020: Alert Service

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-020 |
| **Date** | 2026-07-11 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform has multiple background processes — schema sync, quality scoring, PII detection, schema change tracking — that can produce notable events requiring attention. Rather than each service implementing its own notification mechanism, the platform needs a centralized alerting framework that standardizes alert categories, severity levels, and handler registration.

## Decision

Implement a lightweight pub-sub `AlertService` with:

### Alert Categories

| Category | Description | Source |
|----------|-------------|--------|
| `sync_failure` | Schema sync job failed | Schema sync worker |
| `quality_drop` | Query quality dropped below threshold | Quality Scorer |
| `schema_change` | Schema changed unexpectedly | Schema sync worker |
| `pii_detected` | PII column discovered | PII Detector |
| `stale_data` | Data freshness exceeded threshold | Data freshness monitor |

### Severity Levels

| Severity | Description |
|----------|-------------|
| `critical` | Immediate attention required |
| `high` | Respond within business hours |
| `medium` | Track and review |
| `low` | Informational |

Key design decisions:

- **Pub-sub with callback handlers**: `register_handler()` registers an `AlertHandler` callback. When `emit()` is called, all handlers receive the alert. Handler failures are caught and logged to prevent cascading failures.
- **Convenience methods**: Category-specific methods (`sync_failure_alert()`, `quality_drop_alert()`, etc.) encapsulate alert construction with sensible defaults for severity and message formatting.
- **In-memory alert log**: `get_alerts()` returns emitted alerts with filtering by `tenant_id`, `category`, and `severity`. Useful for dashboards and API responses.
- **`quality_drop_alert()` threshold logic**: Only emits if the score drop exceeds 0.1 threshold. Drops >= 0.3 use `HIGH` severity, otherwise `MEDIUM`.
- **No external dependencies**: Pure in-memory implementation. No database, message queue, or notification service required at this layer.

## Rationale

- **Pub-sub decouples emitters from handlers**: Sync failures, quality drops, and PII detections are produced in different contexts; handlers can be added independently (e.g., email, Slack, PagerDuty) without modifying producer code.
- **In-memory for Sprint 0**: Avoids infrastructure dependency. The in-memory alert log is sufficient for monitoring dashboards during initial development. A persistent alert store and external notification routing are planned for production hardening.
- **Category-specific methods**: Reduce boilerplate and enforce consistent alert structure across the codebase.
- **Handler isolation**: One failing handler must not block other handlers from receiving the alert.

## Consequences

### Positive
- Consistent alert structure across all platform components
- Easy to add new notification channels (slack handler, email handler, PagerDuty handler)
- Filterable alert log enables dashboards and audit trails

### Negative
- In-memory storage means alerts are lost on restart — not suitable for production alerting without persistence
- No built-in notification routing — every handler receives every alert (until filtering is added)
- No deduplication or suppression — repeated alerts are emitted as separate events

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| External alerting system (PagerDuty API, OpsGenie) | Adds external dependency; cannot work offline; not appropriate for Sprint 0 |
| Database-backed alert store | Premature — will be added when alert volume justifies persistence |
| Direct integration per service | Duplicates alert construction, formatting, and routing logic across services |

## References

- `ke/services/alerts.py` — `AlertService`, `Alert`, `AlertSeverity`, `AlertCategory`
- `tests/test_alerts.py` — Tests for all alert types and handler isolation
