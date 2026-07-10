# Workflow Orchestrator Specification

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

**Cross-References**:
- [AI-Agent-Specification.md](AI-Agent-Specification.md) — Agent contracts, pipeline order, QueryState schema
- [API-Specification.md](API-Specification.md) — Endpoint contracts, SSE streaming, error codes
- [Observability-Specification.md](Observability-Specification.md) — Pipeline tracing, metrics, alerting
- [Performance-Budgets.md](Performance-Budgets.md) — End-to-end latency budgets, retry budgets
- [Sequence-Diagrams.md](Sequence-Diagrams.md) — Sequence flows for happy path, error, cold start
- [State-Machines.md](State-Machines.md) — Query state machine, policy enforcement state machine
- [Deployment-Specification.md](Deployment-Specification.md) — Pipeline service deployment, scaling, config

---

## Table of Contents

1. [Overview](#1-overview)
2. [Pipeline Architecture](#2-pipeline-architecture)
3. [Agent Registry](#3-agent-registry)
4. [Pipeline Execution Model](#4-pipeline-execution-model)
5. [QueryState Lifecycle](#5-querystate-lifecycle)
6. [Pipeline Hooks](#6-pipeline-hooks)
7. [Streaming Integration](#7-streaming-integration)
8. [Error Handling & Degradation](#8-error-handling--degradation)
9. [Timeout Management](#9-timeout-management)
10. [Concurrency & Queueing](#10-concurrency--queueing)
11. [Pipeline Metrics](#11-pipeline-metrics)
12. [Configuration](#12-configuration)
13. [Testing](#13-testing)

---

## 1. Overview

The Workflow Orchestrator is the runtime coordinator that wires the 10-agent NL2SQL pipeline into an executable workflow. It is NOT an agent itself — it is the execution framework that manages agent lifecycle, state propagation, error handling, retries, streaming, and metrics collection.

**Key responsibilities**:
- Load and sequence agents according to pipeline definition
- Create, populate, and destroy QueryState objects per query
- Enforce retry budgets, timeout ceilings, and execution order
- Serialize/deserialize state for async execution
- Emit SSE events for streaming clients
- Collect pipeline-level metrics and traces
- Handle graceful degradation — skip non-critical agents when overloaded

**Non-responsibilities**:
- Business logic (all decisions delegated to agents)
- Database connections (handled by Execution Agent)
- Knowledge store access (handled by Retriever and Learning agents)
- User authentication (handled by API Gateway)

---

## 2. Pipeline Architecture

### 2.1 Pipeline Definition

The pipeline is defined as an ordered list of stages. Each stage maps to one agent and has a type (mandatory or optional), retry policy, timeout, and degradation behavior.

```json
{
  "pipeline_id": "v1-full",
  "version": "1.0.0",
  "stages": [
    { "agent": "intent", "mandatory": true, "retries": 2, "timeout_ms": 5000, "degrade": "fail" },
    { "agent": "retriever", "mandatory": true, "retries": 2, "timeout_ms": 10000, "degrade": "fail" },
    { "agent": "planner", "mandatory": true, "retries": 2, "timeout_ms": 15000, "degrade": "fail" },
    { "agent": "generator", "mandatory": true, "retries": 2, "timeout_ms": 30000, "degrade": "fail" },
    { "agent": "validator", "mandatory": true, "retries": 0, "timeout_ms": 5000, "degrade": "fail" },
    { "agent": "repair", "mandatory": false, "retries": 2, "timeout_ms": 10000, "max_iterations": 2, "degrade": "skip" },
    { "agent": "policy_enforcement", "mandatory": true, "retries": 0, "timeout_ms": 5000, "degrade": "fail" },
    { "agent": "execution", "mandatory": true, "retries": 0, "timeout_ms": 60000, "degrade": "fail" },
    { "agent": "reflection", "mandatory": false, "retries": 1, "timeout_ms": 10000, "degrade": "skip" }
  ],
  "post_pipeline": [
    { "agent": "learning", "mandatory": false, "trigger": "batch", "interval_s": 300, "degrade": "skip" }
  ]
}
```

### 2.2 Execution Order

```
     ┌──────────┐
     │  INTENT  │
     └────┬─────┘
          ▼
     ┌──────────┐
     │ RETRIEVER│
     └────┬─────┘
          ▼
     ┌──────────┐
     │ PLANNER  │
     └────┬─────┘
          ▼
     ┌──────────┐
     │ GENERATOR│
     └────┬─────┘
          ▼
     ┌──────────┐      ┌──────────┐
     │VALIDATOR │◄────►│  REPAIR  │
     │          │  max │ (30% of  │
     │          │  2x  │ queries) │
     └────┬─────┘      └──────────┘
          ▼
     ┌──────────┐
     │  POLICY  │
     │ ENFORCEMENT│
     │ (10-layer)│
     └────┬─────┘
          ▼
     ┌──────────┐
     │ EXECUTION│
     │(determin.)│
     └────┬─────┘
          ▼
     ┌──────────┐
     │REFLECTION│
     │(post-exec)│
     └──────────┘

     [Learning Agent runs as batch, every 5 min]
```

### 2.3 Stage States

| State | Description |
|-------|-------------|
| `PENDING` | Stage not yet started |
| `RUNNING` | Agent executing |
| `RETRYING` | Agent failed, retry in progress |
| `SUCCESS` | Agent completed successfully |
| `FAILED` | Agent failed, no retries remain |
| `SKIPPED` | Agent skipped due to degrade policy |
| `TIMEOUT` | Agent exceeded stage timeout |

### 2.4 Pipeline-Level States

| State | Description |
|-------|-------------|
| `QUEUED` | Query accepted but waiting for capacity |
| `PROCESSING` | Pipeline actively executing stages |
| `COMPLETED` | All mandatory stages succeeded |
| `PARTIAL` | Non-mandatory stages failed but mandatory passed |
| `FAILED` | A mandatory stage failed |
| `CANCELLED` | User cancelled or admin terminated |

---

## 3. Agent Registry

### 3.1 Agent Interface

Every agent implements a single interface:

```python
class Agent:
    name: str
    mandatory: bool
    max_retries: int
    timeout_ms: int

    async def process(state: QueryState) -> QueryState:
        """Process the query state. Returns updated state."""
        ...
```

### 3.2 Registry

```python
AGENT_REGISTRY = {
    "intent": IntentAgent(),
    "retriever": RetrieverAgent(),
    "planner": PlannerAgent(),
    "generator": GeneratorAgent(),
    "validator": ValidatorAgent(),
    "repair": RepairAgent(),
    "policy_enforcement": PolicyEnforcementAgent(),
    "execution": ExecutionAgent(),
    "reflection": ReflectionAgent(),
    "learning": LearningAgent(),
}
```

### 3.3 Agent Health Checks

Each agent exposes a `health()` method called by the Orchestrator's readiness probe:

```python
async def health() -> AgentHealth:
    """Returns health status including model availability if applicable."""
    return AgentHealth(
        healthy=True,
        latency_p50_ms=45,
        model_loaded="sqlcoder-7b-2",
        last_error=None
    )
```

The Orchestrator aggregates agent health for the pipeline service's `/healthz` endpoint.

---

## 4. Pipeline Execution Model

### 4.1 Synchronous Execution (Default)

```python
async def execute_pipeline(query_state: QueryState) -> QueryState:
    query_state.pipeline_state = "PROCESSING"
    query_state.timestamps.started_at = now()

    for stage in pipeline.stages:
        agent = AGENT_REGISTRY[stage.agent]

        query_state.current_stage = stage.agent
        query_state = emit_progress(query_state, stage.agent, 0.0)

        for attempt in range(1 + agent.max_retries):
            try:
                query_state = await asyncio.wait_for(
                    agent.process(query_state),
                    timeout=agent.timeout_ms / 1000
                )
                query_state = record_success(query_state, stage.agent, attempt)
                break
            except asyncio.TimeoutError:
                query_state = record_timeout(query_state, stage.agent, attempt)
                if attempt < agent.max_retries:
                    continue
                if agent.mandatory:
                    query_state.pipeline_state = "FAILED"
                    query_state.error = Error(f"Stage {stage.agent} timed out")
                    return query_state
                else:
                    query_state = record_skip(query_state, stage.agent)
                    break
            except Exception as e:
                query_state = record_failure(query_state, stage.agent, str(e), attempt)
                if attempt < agent.max_retries:
                    await asyncio.sleep(ATTEMPT_BACKOFF_MS[attempt] / 1000)
                    continue
                if agent.mandatory:
                    query_state.pipeline_state = "FAILED"
                    query_state.error = Error(f"Stage {stage.agent} failed: {str(e)}")
                    return query_state
                else:
                    query_state = record_skip(query_state, stage.agent)
                    break

        if query_state.pipeline_state == "FAILED":
            return query_state

    query_state.pipeline_state = "COMPLETED"
    query_state.timestamps.completed_at = now()
    emit_metrics(query_state)
    return query_state
```

### 4.2 Async Execution (Queue-Based)

For long-running queries, the Orchestrator returns immediately with a `query_id` and processes the pipeline on a background worker:

```python
async def execute_pipeline_async(query_state: QueryState) -> str:
    query_id = query_state.query_id
    await queue.enqueue(
        queue_name="pipeline",
        payload={"query_id": query_id},
        priority=compute_priority(query_state.tenant_tier)
    )
    return query_id


async def pipeline_worker():
    while True:
        job = await queue.dequeue("pipeline")
        query_state = await load_state(job.query_id)
        query_state = await execute_pipeline(query_state)
        await save_state(query_state)
```

### 4.3 Validator-Repair Loop

The Validator-Repair loop is special: it is the only loop in the pipeline.

```python
for iteration in range(1, MAX_REPAIR_ITERATIONS + 1):
    query_state = await validator.process(query_state)
    if query_state.validation.passed:
        break
    if iteration < MAX_REPAIR_ITERATIONS:
        query_state = await repair.process(query_state)

if not query_state.validation.passed:
    query_state.pipeline_state = "FAILED"
    query_state.error = Error("SQL validation failed after max repair iterations")
    return query_state
```

---

## 5. QueryState Lifecycle

### 5.1 Creation

```json
{
  "query_id": "qry_uuid",
  "tenant_id": "tenant_001",
  "user_id": "usr_001",
  "natural_query": "Show revenue by customer",
  "database_id": "db_001",
  "options": {
    "timeout_seconds": 30,
    "max_rows": 1000,
    "model_tier_preference": null,
    "stream": true
  },
  "pipeline_state": "QUEUED",
  "current_stage": null,
  "stages": {},
  "timestamps": {
    "queued_at": "2026-07-10T12:00:00Z",
    "started_at": null,
    "completed_at": null
  },
  "results": null,
  "error": null,
  "warnings": [],
  "cost_estimate": null
}
```

### 5.2 State Persistence

| Store | Scope | TTL | Purpose |
|-------|-------|-----|---------|
| Redis | In-flight queries | 10 min | Active pipeline state, SSE connections |
| PostgreSQL | Completed queries | 30 days | History, audit, learning |
| Memory (per pod) | Current batch | N/A | Worker-local state during processing |

### 5.3 State Serialization

```python
class QueryState:
    def serialize() -> dict:
        """Serialize to JSON for Redis/PostgreSQL storage."""
        ...

    @classmethod
    def deserialize(data: dict) -> QueryState:
        """Deserialize from JSON, with schema validation."""
        ...

    def validate_schema() -> bool:
        """Ensure all required fields are present and typed correctly."""
        ...
```

### 5.4 Cleanup

After pipeline completion (success or failure), the Orchestrator:

1. Persists final state to PostgreSQL
2. Deletes interim state from Redis
3. Sends final SSE event
4. Triggers post-pipeline hooks

---

## 6. Pipeline Hooks

### 6.1 Pre-Execution Hooks

| Hook | Purpose | Example |
|------|---------|---------|
| `before_pipeline` | Validate input, check rate limits | Ensure tenant not rate-limited |
| `before_stage` | Stage-specific preconditions | Check model availability before generation |
| `after_stage` | Stage completion logging | Emit stage latency metric |

### 6.2 Post-Execution Hooks

| Hook | Purpose | Example |
|------|---------|---------|
| `after_pipeline` | Final metrics, audit log | Emit `pipeline_query_count` |
| `on_failure` | Error notifications | Push to dead-letter queue |
| `on_timeout` | Partial result handling | Return what we have so far |

### 6.3 Hook Registry

```python
HOOKS = {
    "before_pipeline": [rate_limit_check, validate_input],
    "after_pipeline": [emit_metrics, audit_log],
    "on_failure": [dead_letter_queue],
}

async def run_hooks(hook_name: str, context: dict):
    for hook in HOOKS.get(hook_name, []):
        try:
            await hook(context)
        except Exception:
            logger.exception(f"Hook {hook.__name__} failed")
```

---

## 7. Streaming Integration

### 7.1 SSE Event Flow

| Stage | Event Type | Frequency | Payload |
|-------|-----------|-----------|---------|
| Queue | `query.queued` | Once | `{ query_id }` |
| Each stage start | `query.progress` | Once per stage | `{ stage, progress: 0.0 }` |
| Each stage end | `query.progress` | Once per stage | `{ stage, progress: 1.0, latency_ms }` |
| Validation warning | `query.warning` | On detection | `{ warning }` |
| Policy rejection | `policy.warning` | On rejection | `{ layer, reason }` |
| Execution rows | `query.result_chunk` | Every N rows | `{ rows[], columns[] }` |
| Completion | `query.completed` | Once | `{ summary }` |
| Failure | `query.error` | Once | `{ code, message }` |

### 7.2 SSE Manager

```python
class SSEManager:
    connections: dict[str, list[asyncio.Queue]]

    async def subscribe(self, query_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections.setdefault(query_id, []).append(queue)
        return queue

    async def publish(self, query_id: str, event: dict):
        for queue in self.connections.get(query_id, []):
            await queue.put(event)

    async def cleanup(self, query_id: str):
        if query_id in self.connections:
            for queue in self.connections[query_id]:
                await queue.put(None)  # Poison pill
            del self.connections[query_id]
```

### 7.3 Connection Lifecycle

```
Client connects: GET /v1/stream/query/{query_id}
  → SSE connection established
  → Orchestrator sends all buffered events
  → New events published as pipeline progresses
  → Client disconnects: cleanup SSE connection
  → Last client disconnects before pipeline ends:
      pipeline continues (result stored for polling)
```

---

## 8. Error Handling & Degradation

### 8.1 Error Categories

| Category | Examples | Orchestrator Action |
|----------|----------|-------------------|
| Transient | Network timeout, Qdrant connection reset | Retry with backoff |
| Non-retryable | Invalid input, schema validation failure | Fail immediately |
| Degradable | Model timeout, slow retrieval | Skip stage if optional, fallback if available |
| Fatal | Pipeline state corruption, config error | Fail pipeline, alert operator |

### 8.2 Retry Policy

```yaml
retry:
  max_total_retries: 10  # Across all stages
  backoff_strategy: "exponential"
  base_delay_ms: 100
  max_delay_ms: 5000
  jitter: true
  backoff_by_attempt:
    1: 100ms
    2: 500ms
    3: 2000ms
```

### 8.3 Degradation Rules

| Condition | Rule |
|-----------|------|
| Policy Enforcement Agent L1 (Intent Classification) LLM timeout | Skip L1, set default intent to "unknown" |
| Reflection Agent timeout or failure | Skip reflection, continue to response |
| Learning Agent cycle timeout | Skip learning cycle, retry next cycle |
| Generator model escalation fails | Return error, do not attempt lower model |
| Retriever Qdrant timeout (1st retry) | Retry once |
| Retriever Qdrant timeout (2nd retry) | Return cached context, warn user |

### 8.4 Dead-Letter Queue

Queries that fail after exhausting all retries are pushed to a dead-letter queue:

```json
{
  "query_id": "qry_failed_001",
  "tenant_id": "tenant_001",
  "stage": "generator",
  "error": "Model timeout after 2 retries",
  "state_snapshot": { ... },
  "failed_at": "2026-07-10T12:00:00Z",
  "retry_count": 2
}
```

DLQ items are reviewed manually or re-processed after model recovery.

### 8.5 Cancellation

Clients can cancel an in-flight query:

```python
async def cancel_query(query_id: str) -> bool:
    query_state = await load_state(query_id)
    if query_state.pipeline_state not in ["QUEUED", "PROCESSING"]:
        return False
    query_state.pipeline_state = "CANCELLED"
    query_state.error = Error("Query cancelled by user")
    await save_state(query_state)
    await sse_manager.publish(query_id, {
        "type": "query.cancelled",
        "payload": { "query_id": query_id }
    })
    await sse_manager.cleanup(query_id)
    return True
```

---

## 9. Timeout Management

### 9.1 Stage-Level Timeouts

| Stage | Timeout | Rationale |
|-------|---------|-----------|
| Intent | 5s | Simple LLM classification |
| Retriever | 10s | Qdrant + PostgreSQL hybrid search |
| Planner | 15s | LLM plan generation for complex queries |
| Generator | 30s | SQL generation, may run large model |
| Validator | 5s | Deterministic sqlglot parsing |
| Repair | 10s | LLM fix generation |
| Policy Enforcement | 5s | 10 deterministic layers + 1 LLM layer |
| Execution | 60s | Target DB query execution |
| Reflection | 10s | LLM post-execution analysis |

### 9.2 Pipeline-Level Timeout

Total pipeline timeout is computed per query based on options:

```python
pipeline_timeout = min(
    query_state.options.timeout_seconds,
    SUM_OF_MANDATORY_STAGE_TIMEOUTS + BUFFER_SECONDS
)
```

Default: 120 seconds. Beyond this, the pipeline is terminated and a timeout error is returned.

### 9.3 Graceful Timeout Handling

When a stage times out:
1. Cancel the agent's asyncio task
2. Record timeout in stage results
3. If mandatory and no retries remain → pipeline FAILED
4. If optional → skip, mark stage SKIPPED
5. Emit timeout metric

---

## 10. Concurrency & Queueing

### 10.1 Worker Pool

```yaml
pipeline:
  workers:
    default: 50        # Concurrent pipeline executions per pod
    max: 100            # Hard cap
    queue_size: 500     # Max queued queries before rejection
  priority_levels:
    - "enterprise"      # Weight 5, always served
    - "pro"             # Weight 3
    - "starter"         # Weight 1
    - "free"            # Weight 1, rate-limited
```

### 10.2 Queue Implementation

```python
class PriorityQueue:
    queues: dict[int, asyncio.Queue]

    async def enqueue(self, item: QueryTask, priority: int):
        await self.queues[priority].put(item)

    async def dequeue(self) -> QueryTask:
        for priority in sorted(self.queues.keys(), reverse=True):
            try:
                return await asyncio.wait_for(
                    self.queues[priority].get(),
                    timeout=0.1
                )
            except asyncio.TimeoutError:
                continue
        await asyncio.sleep(0.1)
        return await self.dequeue()
```

### 10.3 Rate Limiting

| Level | Queries/min | Burst | Enforced At |
|-------|-------------|-------|-------------|
| Free | 5 | 2 | API Gateway + Orchestrator |
| Starter | 30 | 10 | Orchestrator |
| Pro | 120 | 20 | Orchestrator |
| Enterprise | 500 | 50 | Orchestrator |

The Orchestrator maintains a per-tenant token bucket and rejects queries that exceed the rate limit before queueing.

---

## 11. Pipeline Metrics

### 11.1 Standard Metrics (all stages)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `pipeline_stage_duration_ms` | Histogram | stage, status, model | Per-stage latency |
| `pipeline_stage_attempts` | Counter | stage, status, attempt | Stage execution count |
| `pipeline_total_duration_ms` | Histogram | status | Total pipeline latency |
| `pipeline_queries_queued` | Gauge | priority | Currently queued |
| `pipeline_queries_in_flight` | Gauge | — | Currently executing |
| `pipeline_workers_busy` | Gauge | — | Active workers |
| `pipeline_queue_wait_ms` | Histogram | priority | Time in queue |

### 11.2 Custom Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `pipeline_degraded_stages` | Counter | Stages skipped due to degradation |
| `pipeline_repair_iterations` | Histogram | Repair iterations per query |
| `pipeline_dead_letter_queue_size` | Gauge | DLQ item count |
| `pipeline_cancelled_queries` | Counter | User-cancelled queries |

### 11.3 Tracing

```python
with tracer.start_span("pipeline.execute") as span:
    span.set_attribute("query_id", state.query_id)
    span.set_attribute("tenant_id", state.tenant_id)
    span.set_attribute("model_tier", state.model_used)

    for stage in pipeline.stages:
        with tracer.start_span(f"stage.{stage}") as stage_span:
            stage_span.set_attribute("attempt", attempt)
            state = await execute_stage(stage, state)
            stage_span.set_attribute("status", state.stages[stage].status)
            stage_span.set_attribute("latency_ms", state.stages[stage].latency_ms)
```

---

## 12. Configuration

### 12.1 Pipeline Config (YAML)

```yaml
pipeline:
  version: "1.0.0"
  stages:
    - agent: intent
      mandatory: true
      retries: 2
      timeout_ms: 5000
      degrade: fail
    - agent: retriever
      mandatory: true
      retries: 2
      timeout_ms: 10000
      degrade: fail
    - agent: planner
      mandatory: true
      retries: 2
      timeout_ms: 15000
      degrade: fail
    - agent: generator
      mandatory: true
      retries: 2
      timeout_ms: 30000
      degrade: fail
    - agent: validator
      mandatory: true
      retries: 0
      timeout_ms: 5000
      degrade: fail
    - agent: repair
      mandatory: false
      retries: 2
      timeout_ms: 10000
      max_iterations: 2
      degrade: skip
    - agent: policy_enforcement
      mandatory: true
      retries: 0
      timeout_ms: 5000
      degrade: fail
    - agent: execution
      mandatory: true
      retries: 0
      timeout_ms: 60000
      degrade: fail
    - agent: reflection
      mandatory: false
      retries: 1
      timeout_ms: 10000
      degrade: skip

execution:
  workers: 50
  max_workers: 100
  queue_size: 500
  default_timeout_seconds: 120

retry:
  max_total_retries: 10
  backoff_strategy: exponential
  base_delay_ms: 100
  max_delay_ms: 5000
  jitter: true

priority:
  levels:
    enterprise: { weight: 5, max_concurrent: 20 }
    pro: { weight: 3, max_concurrent: 50 }
    starter: { weight: 1, max_concurrent: 100 }
    free: { weight: 1, max_concurrent: 10, rate_limit_per_min: 5 }

degradation:
  rules:
    - condition: "intent.llm_timeout"
      action: "default_to_unknown"
    - condition: "reflection.timeout"
      action: "skip"
    - condition: "learning.timeout"
      action: "skip_and_retry_next_cycle"
    - condition: "retriever.qdrant_timeout"
      action: "retry_once_then_cached_context"
```

### 12.2 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PIPELINE_WORKERS` | `50` | Concurrent pipeline workers |
| `PIPELINE_QUEUE_SIZE` | `500` | Max queued queries |
| `PIPELINE_DEFAULT_TIMEOUT` | `120` | Default pipeline timeout (s) |
| `PIPELINE_RETRY_MAX` | `10` | Total retries across all stages |
| `PIPELINE_ATTEMPT_BACKOFF_MS` | `[0, 100, 500, 2000]` | Backoff per attempt |

### 12.3 Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `pipeline.reflection.enabled` | `true` | Enable Reflection Agent stage |
| `pipeline.execution.dry_run` | `false` | Skip actual DB execution |
| `pipeline.repair.enabled` | `true` | Enable Validator-Repair loop |
| `pipeline.learning.batch.enabled` | `true` | Enable batch learning loop |

---

## 13. Testing

### 13.1 Unit Tests

| Test | Description |
|------|-------------|
| Stage execution with valid state | Each agent processes valid QueryState |
| Stage execution with invalid state | Agent returns proper error |
| Retry count enforcement | Agent fails exactly N times, pipeline behaves correctly |
| Timeout handling | Stage exceeds timeout, pipeline degrades correctly |
| State serialization round-trip | 1000 random QueryStates serialize/deserialize faithfully |
| Rate limiter | Per-tenant token bucket exhausts, query rejected |

### 13.2 Integration Tests

| Test | Description |
|------|-------------|
| Full pipeline E2E | 100 queries through all stages |
| Pipeline with repair iterations | Query requiring 2 repair cycles |
| Pipeline with policy rejection | Query blocked at policy enforcement |
| Pipeline with stage degradation | Non-mandatory stage fails, pipeline continues |
| Queue priority inversion | Enterprise query dequeued before free query |
| Concurrent pipeline isolation | 10 simultaneous pipelines don't share state |

### 13.3 Chaos Tests

| Test | Description |
|------|-------------|
| Random stage timeout | Random stage times out, verify degradation |
| Random agent failure | Random agent raises exception, verify retry |
| Worker pool exhaustion | Queue fills, verify backpressure |
| Redis failure during pipeline | State persistence fails, verify error handling |
| SSE connection drop | Client disconnects mid-pipeline, verify result stored |
