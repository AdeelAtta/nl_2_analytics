# ADR-018: PII Detection

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-018 |
| **Date** | 2026-07-11 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Enterprise databases often contain columns with Personally Identifiable Information (PII) such as email addresses, phone numbers, Social Security numbers, credit card numbers, and API keys. The platform must detect and classify PII columns during schema introspection to enable security policy enforcement (e.g., restricting queries on sensitive data), monitoring, and compliance reporting. The detector must be fast, deterministic, and work offline without external API calls.

## Decision

Implement a regex-based `PIIDetector` that classifies column names against a curated set of 15 PII categories:

| Category | Sensitivity | Example Patterns |
|----------|-------------|------------------|
| email | HIGH | `email`, `e_mail`, `mail_address` |
| phone | HIGH | `phone`, `mobile`, `cell_phone`, `fax` |
| ssn | CRITICAL | `ssn`, `social_security` |
| credit_card | CRITICAL | `credit_card`, `cc_number`, `pan` |
| password | CRITICAL | `password`, `passwd`, `pwd` |
| api_key | CRITICAL | `api_key`, `api_secret`, `access_key` |
| token | HIGH | `token`, `refresh_token`, `auth_token` |
| ip_address | MEDIUM | `ip_address`, `client_ip`, `remote_addr` |
| date_of_birth | HIGH | `date_of_birth`, `dob`, `birth_date` |
| address | MEDIUM | `address`, `street`, `city`, `state`, `zip`, `postal_code` |
| name | MEDIUM | `first_name`, `last_name`, `full_name` |
| bank_account | CRITICAL | `bank_account`, `routing_number`, `account_number` |
| health | CRITICAL | `health_condition`, `diagnosis`, `medical_record` |
| financial | MEDIUM | `salary`, `income`, `credit_score`, `annual_revenue` |
| location | MEDIUM | `latitude`, `longitude`, `gps_coordinates` |

Key design decisions:

- **Regex-based matching on column names**: Fast, deterministic, no external dependencies. Patterns use word-boundary matching to avoid false positives.
- **Sensitivity levels**: Each category has a sensitivity level (CRITICAL, HIGH, MEDIUM) enabling differentiated policy enforcement.
- **Bulk classification**: `classify_columns()` accepts a list of `Column` objects and returns per-column classification metadata.
- **Summary reporting**: `summarize()` produces aggregate statistics (total PII columns, percentage, breakdown by category and sensitivity).
- **Multi-tenant**: Classification is scoped by tenant for isolation.

## Rationale

- **Regex beats ML for column name classification**: Column naming conventions are finite and domain-specific. A curated pattern list is more accurate and much faster than a trained classifier.
- **No external dependencies**: Works offline and in air-gapped deployments. No API calls or model loading required.
- **15 categories cover enterprise needs**: Based on common compliance frameworks (GDPR, HIPAA, PCI-DSS, SOC 2).
- **Sensitivity levels enable graduated response**: CRITICAL columns might be blocked from queries entirely, while MEDIUM columns might only trigger an audit log entry.
- **Bulk + summary APIs**: Bulk for real-time schema sync, summary for compliance dashboards and reporting.

## Consequences

### Positive
- Zero-dependency, sub-millisecond classification per column
- Deterministic results — no false positives from ML drift
- Works fully offline and in air-gapped environments

### Negative
- Only classifies by column name; cannot detect PII in column data values without a separate data-scanning pipeline
- Pattern list requires maintenance as new PII categories emerge
- Regex may miss obfuscated or unconventional column names

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| ML-based classifier (e.g., spaCy NER) | Heavy dependency, slower, requires GPU for throughput, less accurate on column names vs natural text |
| Data-scanning PII detection | Much higher cost and latency; suitable as a separate batch process but not for real-time schema sync |
| Third-party API | Cannot work offline; introduces cost per classification and external dependency |

## References

- `ke/services/pii.py` — `PIIDetector`, `PIIPattern`, `_PII_RULES`
- `tests/test_pii_detector.py` — Comprehensive tests for all 15 categories
- `ke/services/alerts.py` — `pii_detected_alert()` integration
