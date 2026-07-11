# ADR-021: Multi-Turn Session

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-021 |
| **Date** | 2026-07-11 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Users often ask follow-up questions that depend on previous context — "What were the top 5 products last quarter?" followed by "Show me their month-over-month trend." Without conversation history, each query is treated independently, losing contextual references, table aliases, and intent continuity. The platform must support multi-turn conversations where each turn can reference prior queries, results, and intents.

## Decision

Implement an `InMemorySessionService` that maintains conversational context across turns:

### Session Model

| Component | Description |
|-----------|-------------|
| `SessionTurn` | Data class with `query`, `sql`, `result_summary`, `intent_type`, `model_tier`, `model_name`, `created_at` |
| `Session` | Collection of turns belonging to one conversation, with a max of 20 turns |
| `InMemorySessionService` | Singleton service managing `get_or_create()`, `add_turn()`, `format_history()` |

### Pipeline Integration

The `PipelineOrchestrator` integrates session support at three points:

1. **Context injection** (before generation): `session_service.format_history()` produces a `conversation_history` string injected into `merged_context`. This string contains prior turns formatted as `User: ...`, `Assistant: SELECT ...`, `Result: ...` pairs.
2. **Turn recording** (after execution): `session_service.add_turn()` saves the current query, SQL, result summary, intent, and model metadata.
3. **Session ID propagation**: `PipelineResult.session_id` carries the session ID back to the client for subsequent requests.

Key design decisions:

- **In-memory storage**: Sessions are stored in a `dict[str, Session]` in process memory. No persistence across restarts. Suitable for development and single-instance deployments.
- **Context window**: History is injected as a formatted string into the LLM prompt context, limited to 20 turns. This prevents unbounded prompt growth and manages token costs.
- **Intent continuation**: Each turn records the detected intent type (`SELECT`, `AGGREGATE`, `JOIN`, `TIME_SERIES`, etc.), enabling the pipeline to disambiguate follow-ups.
- **Singleton by default**: The API endpoint creates a module-level `InMemorySessionService` singleton, shared across requests for the process lifetime.

## Rationale

- **In-memory is sufficient for Sprint 0**: Session data is ephemeral by nature; persistence is not required for development. A future ADR will address persistent session storage (Redis or PostgreSQL) for production.
- **Context string injection**: The simplest integration point — no changes to the LLM interface. The history is injected into the same context object used for schema and policy information.
- **20-turn limit**: Based on observed usage patterns — most sessions complete within 3-5 turns. 20 turns at ~500 tokens each would use ~10K tokens (well within most model context windows).
- **Singleton avoids connection pooling**: No database connections needed. Sessions are lightweight data classes.

## Consequences

### Positive
- Enables natural follow-up queries without repeating context
- Simple in-memory implementation with zero infrastructure dependencies
- Pipeline integration is clean and non-invasive
- Session ID propagation enables client-side continuity

### Negative
- Sessions are lost on process restart (acceptable for development)
- In-memory storage does not scale horizontally — sessions are local to each instance
- No session expiry — abandoned sessions remain in memory until process restart
- Context string grows with each turn, increasing token usage

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Redis-backed sessions | Unnecessary for Sprint 0; will be added when horizontal scaling is needed |
| Database-backed sessions | Adds latency and migration overhead; sessions are ephemeral and do not need durability |
| No session support | Users would need to repeat context in every query — poor UX for follow-ups |
| LlamaIndex-style conversation memory | Adds a framework dependency; the in-memory service provides equivalent functionality with less abstraction |

## References

- `ke/services/session.py` — `InMemorySessionService`, `SessionTurn`
- `ke/services/pipeline.py` — Context injection and turn recording in `PipelineOrchestrator.execute()`
- `ke/api/routes/query.py` — Session singleton and session_id propagation
- `tests/test_session.py` — Tests for session lifecycle and pipeline integration
