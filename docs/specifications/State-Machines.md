# State Machines

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

---

## 1. Query Lifecycle State Machine

```
                    ┌──────────────────────────────────────────┐
                    │               NEW                          │
                    │  User submits query                       │
                    └────────────────┬─────────────────────────┘
                                     │
                                     ▼
                    ┌──────────────────────────────────────────┐
                    │           INTENT_CLASSIFYING               │
                    │  Intent Agent analyzes query              │
                    └────────────────┬─────────────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                          ▼                     ▼
              ┌──────────────────────┐  ┌──────────────────────┐
              │   CONTEXT_RETRIEVING │  │    INTENT_FAILED     │
              │  Retriever fetches   │  │  Intent classification│
              │  relevant schema     │  │  failed               │
              └──────────┬───────────┘  └──────────┬───────────┘
                         │                         │
                         ▼                         ▼
              ┌──────────────────────┐     ┌──────────────┐
              │     PLANNING         │     │   FAILED     │
              │  Planner builds SQL  │     │  Return      │
              │  query plan          │     │  ERR-014     │
              └──────────┬───────────┘     └──────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
    ┌──────────────────┐   ┌──────────────────┐
    │   GENERATING      │   │   PLAN_FAILED    │
    │  NL2SQL generation │   │  Plan infeasible  │
    └────────┬─────────┘   └──────────────────┘
             │
             ▼
    ┌──────────────────┐
    │   VALIDATING      │
    │  Validation Agent │
    └────────┬─────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│  REPAIR  │    │ VALID    │
│ (max 2x) │    │ SQL OK   │
└────┬─────┘    └────┬─────┘
     │               │
     └───────┐       │
             ▼       ▼
    ┌──────────────────────┐
     │    POLICY_CHECK       │
     │  10-layer policy enf.│
     └──────────┬───────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
 ┌──────────────┐  ┌──────────────┐
 │  POLICY      │  │   EXECUTING  │
 │  REJECTED    │  │  Execute SQL │
 │  ERR-012     │  │  against DB  │
 └──────────────┘  └──────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       ┌──────────────┐    ┌──────────────┐
       │   SUCCESS     │    │  EXECUTION   │
       │  Results      │    │  FAILED      │
       │  returned     │    │  ERR-009/010 │
       └──────┬───────┘    └──────────────┘
              │
              ▼
       ┌──────────────┐
       │  FEEDBACK     │
       │  Awaiting     │
       │  user rating  │
       └──────┬───────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌────────────┐ ┌────────────┐
│  ARCHIVED  │ │  LEARNING  │
│ (no rating)│ │ (feedback  │
│            │ │ given)     │
└────────────┘ └────────────┘
```

### States Summary

| State | Description | Entered Via | Can Exit To |
|-------|-------------|-------------|-------------|
| NEW | Query submitted, not yet processed | User submits | INTENT_CLASSIFYING |
| INTENT_CLASSIFYING | Intent Agent processing | NEW | CONTEXT_RETRIEVING, INTENT_FAILED |
| INTENT_FAILED | Intent classification failed | INTENT_CLASSIFYING | FAILED |
| CONTEXT_RETRIEVING | Retriever fetching context | INTENT_CLASSIFYING | PLANNING |
| PLANNING | Planner building query plan | CONTEXT_RETRIEVING | GENERATING, PLAN_FAILED |
| PLAN_FAILED | Query plan infeasible | PLANNING | FAILED |
| GENERATING | NL2SQL model generating SQL | PLANNING | VALIDATING |
| VALIDATING | Validation Agent checking SQL | GENERATING | REPAIR, POLICY_CHECK |
| REPAIR | Repair Agent fixing errors | VALIDATING | VALIDATING (max 2 cycles) |
| POLICY_CHECK | 10-layer policy enforcement processing | VALIDATING | EXECUTING, POLICY_REJECTED |
| POLICY_REJECTED | Policy enforcement blocked query | POLICY_CHECK | FAILED |
| EXECUTING | SQL executing against target DB | POLICY_CHECK | SUCCESS, EXECUTION_FAILED |
| EXECUTION_FAILED | Target DB execution error | EXECUTING | FAILED |
| SUCCESS | Query completed with results | EXECUTING | FEEDBACK |
| FEEDBACK | Awaiting user rating | SUCCESS | ARCHIVED, LEARNING |
| LEARNING | Feedback sent to learning loop | FEEDBACK | ARCHIVED |
| ARCHIVED | Terminal state | FEEDBACK, LEARNING | — |
| FAILED | Terminal error | *FAILED states | — |

## 2. Schema Sync State Machine

```
PENDING ──(sync triggered)──> SYNCING ──(success)──> SYNCED
  ^                              │                       │
  │                              │                       │
  │                              ▼                       │
  │                          ERROR ──(retry, 3x max)──> SYNCING
  │                              │                       │
  │                              ▼                       │
  │                          FAILED ──(manual retry)──> PENDING
  │                                                      │
  └─────────────────────(24h poll or DDL trigger)────────┘
```

## 3. Policy Enforcement State Machine (per layer)

```
PENDING ──> CHECKING ──> PASSED ──> NEXT LAYER
                            │
                            │
                            ▼
                         FAILED ──> CHAIN STOPS (fail-closed)
```

## 4. Feedback Item State Machine

```
CREATED ──(polled by learning loop)──> VALIDATING ──(quality > 0.3)──> PROCESSING ──> COMPLETED
                                              │                              │
                                              │                              │
                                              ▼                              ▼
                                        REJECTED ──> ARCHIVED          FAILED ──> ARCHIVED
```

## 5. Tenant Provisioning State Machine

```
PENDING (registered, not ready)
    │
    │ (schema sync first)
    ▼
PROVISIONING (creating Qdrant collection, PG schema)
    │
    │
    ▼
ACTIVE (ready to serve queries)
    │
    │ (admin action)
    ▼
SUSPENDED (rate limit exceeded, payment failed)
    │
    │ (payment received / admin restore)
    ▼
ACTIVE
    │
    │ (deletion requested)
    ▼
DELETING (cleanup: drop Qdrant collection, delete PG data)
    │
    │
    ▼
DELETED (terminal: 30-day soft delete window expired)
```

## 6. Model Tier Selection State Machine

```
START ──> EVALUATE_COMPLEXITY
              │
      ┌───────┼───────┐
      ▼       ▼       ▼
   SIMPLE  MEDIUM  COMPLEX
      │       │       │
      ▼       ▼       ▼
 SQLCoder  Qwen2.5  DeepSeek
   7b-2     72B      V3
      │       │       │
      └───────┼───────┘
              │
              ▼
         ┌─────────┐
         │ FALLBACK│──> GPT-4o (if primary unavailable)
         └─────────┘
              │
              ▼
           RETURN
```

## 7. Cache Lifecycle State Machine

```
COLD (no data) ──(query executed)──> WARM ──(TTL expired)──> COLD
                                          │
                                          │ (schema change)
                                          ▼
                                     INVALIDATED ──> COLD
```
