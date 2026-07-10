# Agent: Query Pipeline

| Metadata | Value |
|----------|-------|
| **Agent ID** | AGENT-PIPELINE |
| **Owns Epics** | EP-007, EP-008, EP-009, EP-010, EP-011 |
| **Workspace** | `/backend/query-pipeline/` |
| **Reads** | `/docs/Component-Design.md`, `/docs/Data-Flow.md`, `/docs/epics/EP-007`-EP-011 |

---

## Responsibilities

1. Implement Context Retrieval Agent (hybrid search + ranking + deduplication)
2. Implement Intent Analysis Agent (classify user intent)
3. Implement Query Planning Agent (plan SQL approach)
4. Implement NL2SQL Generation pipeline (LangGraph, multi-candidate, tiered routing)
5. Implement Policy Enforcement Agent (10-layer fail-closed stack)
6. Implement Reflection Agent (self-critique)
7. Implement Repair Agent (common error fixes)
8. Implement Query Executor (safe SQL execution + result formatting)
9. Build inference abstraction layer (vLLM, SGLang, OpenAI, Anthropic)
10. Implement model router and cost tracking

## Workspace Boundaries

```
/backend/query-pipeline/
  __init__.py
  /intent/
    intent_agent.py         -> Intent classification
  /retrieval/
    retriever.py            -> Context retrieval agent
    ranker.py               -> Context ranking
  /planner/
    planner.py              -> Query planner
    plan_validator.py       -> Plan feasibility check
  /generator/
    router.py               -> Model router
    /candidates/
        generator.py        -> Multi-candidate generator
        selector.py         -> Candidate selector
    /models/
        sqlcoder.py         -> SQLCoder-7b-2 wrapper
        qwen.py             -> Qwen2.5-72B wrapper
        deepseek.py         -> DeepSeek-V3 wrapper
        gpt4o.py            -> GPT-4o fallback wrapper
    /agents/
        reflection.py       -> Reflection agent
        repair.py           -> Repair agent
    orchestrator.py         -> LangGraph pipeline orchestrator
  /policy/
    chain.py                -> Policy enforcement chain framework
    layers/
        intent_classification.py   -> L1: Intent classification (LLM)
        sql_sanitization.py         -> L2: SQL injection prevention
        rbac.py                     -> L3: Schema access control
        cost_ceiling.py             -> L4: Cost guardrail
        sql_validation.py           -> L5: Syntax + semantic validation
        read_only.py                -> L6: DDL/DML blocking
        audit_logging.py            -> L7: Audit trail
        data_classification.py      -> L8: PII detection, cross-tenant check
        advanced_validation.py      -> L9: Allowlist, dangerous functions, quotas
        anomaly_detection.py        -> L10: Query baseline comparison
  /executor/
    connection_pool.py
    executor.py
    formatter.py
    error_handler.py
  /shared/
    inference.py            -> Inference abstraction layer
    cost_tracker.py         -> Cost tracking
```

## DO NOT Touch

- `/backend/ke/`
- `/backend/schema-intelligence/`
- `/backend/api/`
- `/backend/learning/`
- `/frontend/`
- `/infra/`

## Prompts

### LangGraph Pipeline Prompt
```
Implement the LangGraph NL2SQL pipeline orchestrator.

Create orchestrator.py with:
- StateGraph defining the 10-agent pipeline
- Nodes: intent -> retrieval -> planner -> generator -> [validator -> repair]² -> policy_enforcement -> execution -> reflection
- Learning Agent: batch-only, runs every 5 min outside main pipeline graph
- Conditional edges: if validation fails -> repair (max 2 cycles)
- Policy enforcement: 10-layer fail-closed chain (L1: intent classification via LLM, L2-L10: fully deterministic)
- Execution: deterministic SQL executor (connection pool, timeout, result normalization)
- State class: QueryState (user_query, context, sql_candidates, policy_results, execution, errors, cost, metadata)

Reference EP-009, EP-010, and Component-Design.md for agent details.

Each agent should:
- Have a clear input schema, output schema, and failure mode
- Log execution time and cost
- Handle errors gracefully (return to previous node with error info)
```

## Definition of Done
- Full 10-agent pipeline end-to-end tested
- Policy enforcement stack blocks all security threats
- Inference abstraction layer works with vLLM + OpenAI
- Model router selects correct tier for 90%+ of queries
- All task status files updated
