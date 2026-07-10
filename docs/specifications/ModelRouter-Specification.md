# Model Router Specification

**Enterprise Data Intelligence Platform — Intelligent Model Routing Subsystem**

| Metadata | Value |
|----------|-------|
| **Author** | Principal AI Platform Architect |
| **Date** | 2026-07-10 |
| **Status** | Approved |
| **Version** | 1.0 |
| **Architecture Reference** | System-Architecture.md §3, Component-Design.md §5, Architecture-Review.md §10.8 |
| **ADR References** | ADR-008 (Tiered Model Routing), ADR-009 (Self-Hosted Inference Primary) |
| **Cross-References** | AI-Agent-Specification.md §2, Performance-Specification.md §5, Infrastructure-Specification.md §17-19, KnowledgeEngine-Specification.md §9 |

---

## Table of Contents

1. [Routing Philosophy](#1-routing-philosophy)
2. [System Context](#2-system-context)
3. [Architecture](#3-architecture)
4. [Model Registry](#4-model-registry)
5. [Capability-Based Routing](#5-capability-based-routing)
6. [Cost-Aware Routing](#6-cost-aware-routing)
7. [Latency-Aware Routing](#7-latency-aware-routing)
8. [Complexity Estimation](#8-complexity-estimation)
9. [Confidence Scoring](#9-confidence-scoring)
10. [Fallback Strategy](#10-fallback-strategy)
11. [Provider Abstraction Layer](#11-provider-abstraction-layer)
12. [Local Model Inference](#12-local-model-inference)
13. [Cloud Model Gateway](#13-cloud-model-gateway)
14. [AMD ROCm Integration](#14-amd-rocm-integration)
15. [NVIDIA Compatibility](#15-nvidia-compatibility)
16. [Routing API](#16-routing-api)
17. [Cache Strategy](#17-cache-strategy)
18. [Metrics and Monitoring](#18-metrics-and-monitoring)
19. [Testing Strategy](#19-testing-strategy)
20. [Failure Handling](#20-failure-handling)
21. [Security Considerations](#21-security-considerations)
22. [Future Improvements](#22-future-improvements)

---

## 1. Routing Philosophy

### 1.1 Principles

| Principle | Description |
|-----------|-------------|
| **Right model, right query** | Every query should be handled by the cheapest model capable of producing a correct result, not the most powerful one available |
| **Cost as a first-class signal** | Routing decisions explicitly trade off accuracy, latency, and cost — with hard cost ceilings per query |
| **Graceful degradation** | When a model fails (quality, timeout, outage), the router escalates to the next capable tier — never returns error without attempting alternatives |
| **Extensibility over hardcoding** | Models, providers, and routing policies are configured through the Model Registry — adding a new model never requires code changes |
| **Observability as prerequisite** | Every routing decision is logged with its rationale, cost, and outcome — enabling continuous optimization |
| **Tenant-aware fairness** | Routing respects tenant cost tiers (Starter/Pro/Enterprise) — a Starter tenant never routes to the most expensive model |

### 1.2 Scope

The Model Router decides **which model** processes a given query. It does NOT:

| Out of Scope | Handled By |
|-------------|------------|
| Intent classification | Intent Agent (AI-Agent-Spec.md §2) |
| Query planning | Planner Agent (AI-Agent-Spec.md §4) |
| SQL generation | Generator Agent (AI-Agent-Spec.md §5) |
| SQL validation | Validator Agent (AI-Agent-Spec.md §6) |
| Result caching | Context Layer / KE Cache |
| GPU scheduling | K8s scheduler + node pool assignment |

### 1.3 Design Tenets

- **Zero hardcoded model names**: All models are registered in the Model Registry. The router references models by capability profile, not name.
- **Pluggable routing strategies**: The default strategy is rules-based (MVP), but strategies are swappable — learned routing, ensemble routing, and policy-based routing are strategy implementations, not rewrites.
- **Async by default**: All routing decisions are asynchronous to avoid blocking the query pipeline on slow routing evaluation.
- **Routing < 5ms P99**: Routing overhead must be negligible relative to model inference latency (800ms-8s).

---

## 2. System Context

### 2.1 Router Position in Query Pipeline

```
User Query
    │
    ▼
┌──────────────────┐
│  API Gateway     │  (auth, rate limit, tenant context)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Intent Agent    │  (classify intent, extract entities, estimate complexity)
└──────┬───────────┘
       │ query_intent + complexity_score
       ▼
┌──────────────────┐
│  Model Router    │  ◄── THIS SYSTEM
│  (select model)  │
└──────┬───────────┘
       │ model_selection
       ▼
┌──────────────────┐
│  Retriever       │  (fetch context — uses model_selection to tune context budget)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Planner Agent   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Generator Agent │  (generates SQL using selected model)
└──────┬───────────┘
       │
       ▼
   [Validation + Repair + Reflection]
```

### 2.2 Integration Points

| Component | Integration | Direction |
|-----------|-------------|-----------|
| Intent Agent | Receives `QueryIntent` (intent type, complexity, entities) | Input |
| Retriever | Receives model tier — adjusts context budget (simpler models need more context) | Output |
| Generator Agent | Receives selected `ModelDescriptor` — knows which endpoint to call | Output |
| Model Registry | Reads registered models and their capability profiles | Internal |
| Provider Abstraction | Routes inference calls to the correct provider backend | Internal |
| KE Metrics | Writes routing decisions, latency, cost per query | Output |

---

## 3. Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Model Router Service                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │             Router Orchestrator                    │    │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────┐   │    │
│  │  │Strategy │  │Fallback  │  │Decision Logger │   │    │
│  │  │Selector │──│Executor  │──│ + Metrics      │   │    │
│  │  └────┬────┘  └──────────┘  └────────────────┘   │    │
│  │       │                                            │    │
│  │       ▼                                            │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │          Routing Strategy Chain               │  │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │    │
│  │  │  │Rules     │→ │Cost      │→ │Latency     │  │  │    │
│  │  │  │Strategy  │  │Awareness │  │Awareness   │  │  │    │
│  │  │  └──────────┘  └──────────┘  └────────────┘  │  │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │    │
│  │  │  │Capability│→ │Tenant    │→ │Confidence  │  │  │    │
│  │  │  │Matcher   │  │Policy    │  │Gate        │  │  │    │
│  │  │  └──────────┘  └──────────┘  └────────────┘  │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────┐  ┌─────────────────────────────┐   │
│  │  Model Registry   │  │  Provider Abstraction Layer │   │
│  │  (in-memory +     │  │  ┌────────┐ ┌───────────┐  │   │
│  │   PG-backed)      │  │  │Local   │ │Cloud API  │  │   │
│  │                   │  │  │Backend │ │Gateway    │  │   │
│  │  • Model profiles  │  │  └────────┘ └───────────┘  │   │
│  │  • Capability maps │  │  ┌────────┐ ┌───────────┐  │   │
│  │  • Health status   │  │  │ Mock   │ │Future     │  │   │
│  │  • Cost tables     │  │  │Backend │ │Backend    │  │   │
│  └──────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Service Configuration

| Property | Value |
|----------|-------|
| **Service name** | `model-router` |
| **Port** | 8300 (gRPC), 8301 (HTTP health) |
| **Deployment** | Kubernetes Deployment (CPU-only) |
| **Replicas** | 2-4 (HPA-based on request rate) |
| **Resources** | 500m CPU, 512MB RAM (no GPU) |
| **State** | Stateless (state in Model Registry backend) |
| **Language** | Python 3.12 |

### 3.3 Data Flow

```
1. Router receives QueryIntent from Intent Agent
2. Strategy Selector picks routing strategy (tenant-configurable)
3. Strategy chain evaluates:
   a. Capability Matcher: which models CAN handle this query?
   b. Cost Awareness: filter by cost ceiling
   c. Latency Awareness: filter by latency budget
   d. Tenant Policy: apply tenant-specific overrides
   e. Confidence Gate: ensure minimum confidence for selected model
4. Fallback Executor: if primary selection fails, execute fallback chain
5. Decision Logger: write routing decision to KE Metrics
6. Return ModelSelection to pipeline
```

### 3.4 Request Flow Sequence

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌────────────┐    ┌──────────────┐
│ Intent   │    │Model     │    │ Model     │    │ Provider    │    │ Generator    │
│ Agent    │    │Router    │    │ Registry  │    │ Abstraction │    │ Agent        │
└────┬─────┘    └────┬─────┘    └─────┬─────┘    └──────┬─────┘    └──────┬───────┘
     │                │                │                  │                 │
     │ QueryIntent    │                │                  │                 │
     │───────────────>│                │                  │                 │
     │                │ GetCandidates() │                 │                 │
     │                │───────────────>│                  │                 │
     │                │ ModelProfiles  │                  │                 │
     │                │<───────────────│                  │                 │
     │                │                │                  │                 │
     │                │ Evaluate Strategies               │                 │
     │                │──────────────────                 │                 │
     │                │                │                  │                 │
     │                │ Filter by capability              │                 │
     │                │ Filter by cost ceiling            │                 │
     │                │ Filter by latency budget          │                 │
     │                │ Apply tenant policy               │                 │
     │                │ Verify confidence threshold       │                 │
     │                │──────────────────                 │                 │
     │                │                │                  │                 │
     │                │ Check Model Health                │                 │
     │                │───────────────>│                  │                 │
     │                │ Health Status  │                  │                 │
     │                │<───────────────│                  │                 │
     │                │                │                  │                 │
     │ ModelSelection │                │                  │                 │
     │<───────────────│                │                  │                 │
     │                │                │                  │                 │
     │ (pipeline continues with selected model)            │                 │
     │                │                │                  │                 │
     │                │  (if primary fails)               │                 │
     │                │  ExecuteFallback()                │                 │
     │                │──────────────────                 │                 │
```

---

## 4. Model Registry

### 4.1 Registry Concept

The Model Registry is the single source of truth for all models available to the routing system. It decouples the routing logic from specific model names — the router evaluates capability profiles, not model IDs.

### 4.2 Model Profile Schema

```json
{
  "model_id": "sqlcoder-7b-2",
  "name": "SQLCoder-7B-v2",
  "version": "2.0",
  "family": "sqlcoder",
  "parameters_b": 7,
  "status": "active",
  "provider": {
    "type": "local",
    "endpoint": "http://inference-sqlcoder:8000/v1/completions",
    "health_endpoint": "http://inference-sqlcoder:8000/health",
    "gpu_required": true,
    "gpu_memory_gb": 16
  },
  "capabilities": {
    "intent_types": ["select", "aggregate", "filter"],
    "max_tables": 2,
    "max_joins": 0,
    "supports_subqueries": false,
    "supports_cte": false,
    "supports_window_functions": false,
    "supports_set_operations": false,
    "supports_cross_db": false,
    "supports_ddl": false,
    "max_query_complexity": 0.3,
    "dialects": ["postgresql", "mysql", "sqlite"]
  },
  "cost": {
    "per_request": 0.0003,
    "per_input_token": 0.000001,
    "per_output_token": 0.000003,
    "currency": "USD"
  },
  "latency": {
    "p50_ms": 800,
    "p95_ms": 1200,
    "p99_ms": 2000,
    "first_token_p50_ms": 200,
    "first_token_p95_ms": 400
  },
  "confidence": {
    "mean": 0.85,
    "min_acceptable": 0.70
  },
  "limits": {
    "max_input_tokens": 4096,
    "max_output_tokens": 1024,
    "max_concurrent": 128,
    "rate_per_second": 24
  },
  "metadata": {
    "provider_name": "self-hosted (AMD ROCm)",
    "deployed_at": "2026-07-10T00:00:00Z",
    "last_accuracy_eval": 0.87,
    "notes": "Primary model for simple queries. 8 pods per MI300X."
  }
}
```

### 4.3 Registry Storage

| Store | Purpose | Freshness |
|-------|---------|-----------|
| **PostgreSQL** (source of truth) | Persistent model registry — profiles, cost tables, history | N/A |
| **In-memory cache** (Router service) | Hot cache for routing decisions | < 60s stale |
| **Redis** (distributed cache) | Cross-pod model registry cache | < 60s stale |

### 4.4 Registry API (Internal)

| Operation | Method | Description |
|-----------|--------|-------------|
| List models | `GET /v1/models` | List all active models with capability summaries |
| Get model | `GET /v1/models/{model_id}` | Full model profile |
| Register model | `POST /v1/models` | Add new model to registry |
| Update model | `PUT /v1/models/{model_id}` | Update profile (capabilities, cost, status) |
| Deregister model | `DELETE /v1/models/{model_id}` | Soft-delete (mark inactive) |
| Health check | `GET /v1/models/{model_id}/health` | Get current health status |

### 4.5 Health Tracking

Each model has a health status that the router checks before routing:

| Status | Meaning | Routing Behavior |
|--------|---------|------------------|
| `healthy` | Model responding normally | Route normally |
| `degraded` | Model responding but high latency or error rate > 5% | Route to this model only if no alternative in same capability tier |
| `unhealthy` | Model not responding or error rate > 20% | Never route — skip in fallback chain |
| `maintenance` | Model being updated | Temporarily remove from routing |
| `deprecated` | Model scheduled for removal | Route only if no alternative exists — log warning |

Health is determined by:
- Periodic health probes (every 30s)
- Request success rate (rolling 5-minute window)
- P95 latency (rolling 5-minute window)
- Queue depth at inference endpoint

---

## 5. Capability-Based Routing

### 5.1 Concept

Every model declares what it can do in its capability profile. The router matches query requirements against model capabilities — a model is eligible only if it can handle ALL required capabilities for the query.

### 5.2 Capability Dimensions

| Dimension | Values | Example |
|-----------|--------|---------|
| **Intent types** | select, aggregate, filter, join, nested, set_op, ddl | Aggregate query requires `aggregate` capability |
| **Max tables** | 1, 2, 4, 8, unlimited | 3-table join requires `max_tables >= 3` |
| **Max joins** | 0, 1, 2, 4, unlimited | 3-way join requires `max_joins >= 2` |
| **SQL features** | subquery, cte, window_function, set_operation, cross_db | CTE query requires `supports_cte = true` |
| **Dialects** | postgresql, mysql, sqlserver, bigquery, snowflake, sqlite | SQL Server query requires dialect support |
| **Max complexity** | 0.0 - 1.0 scale | Query with complexity 0.7 routed to model with `max_query_complexity >= 0.7` |

### 5.3 Capability Matching Algorithm

```
function find_capable_models(query_intent, model_registry):
    candidates = []

    for model in model_registry.active_models():
        if not model.supports_dialect(query_intent.dialect):
            continue
        if model.max_tables < query_intent.table_count:
            continue
        if model.max_joins < query_intent.join_count:
            continue
        if query_intent.requires_cte and not model.supports_cte:
            continue
        if query_intent.requires_window and not model.supports_window_functions:
            continue
        if query_intent.requires_subquery and not model.supports_subqueries:
            continue
        if query_intent.complexity_score > model.max_query_complexity:
            continue
        if query_intent.intent_type not in model.intent_types:
            continue

        candidates.append(model)

    return sorted(candidates, key=lambda m: m.cost.per_request)
```

### 5.4 Capability Versioning

Models improve over time (fine-tuning, new versions). Capabilities are versioned:

| Version Change | Registry Update | Impact |
|----------------|----------------|--------|
| New capability | Update profile capabilities | Router automatically considers model for new query types |
| Capability removal | Update profile capabilities | Router excludes model from affected queries |
| Accuracy improvement (released) | Update `last_accuracy_eval` | Confidence scoring adjusts accordingly |
| Cost reduction (optimization) | Update cost profile | Cost-aware routing shifts traffic |

---

## 6. Cost-Aware Routing

### 6.1 Cost Model

Every query has three cost dimensions that the router must balance:

| Cost Type | Description | Bounds |
|-----------|-------------|--------|
| **Inference cost** | Direct LLM inference cost (self-hosted GPU or API) | $0.0003 - $0.02 per query |
| **Latency cost** | User wait time — amortized cost of slower response | Implicit (captured in latency budget) |
| **Retry cost** | Cost of regeneration if model produces invalid SQL | $0.0003 - $0.04 (worst case) |

### 6.2 Cost Ceiling Enforcement

Each query has a hard cost ceiling determined by source:

| Source | Ceiling Logic |
|--------|---------------|
| **Tenant tier** | Starter: $0.005/query max. Pro: $0.02/query max. Enterprise: $0.10/query max. |
| **User preference** | User can set per-query budget override (Enterprise only) |
| **System default** | $0.02/query max (equivalent to one GPT-4o call) |
| **Escalation budget** | Additional $0.02 for fallback chain (2 escalations max) |

### 6.3 Cost-Aware Selection

Among capable models, the router selects the cheapest model that:
1. Meets capability requirements
2. Has confidence >= min_acceptable for the query type
3. Is healthy (not degraded or unhealthy)
4. Fits within the tenant's cost ceiling

```
function select_cheapest_capable(capable_models, query_intent, tenant_policy):
    cost_ceiling = tenant_policy.cost_ceiling(query_intent)

    affordable = [
        m for m in capable_models
        if m.cost.per_request <= cost_ceiling
        and m.confidence.mean >= m.confidence.min_acceptable
        and m.health.status == "healthy"
    ]

    if not affordable:
        # Relax confidence requirement for degraded models
        affordable = [
            m for m in capable_models
            if m.cost.per_request <= cost_ceiling * 1.5
            and m.health.status in ("healthy", "degraded")
        ]

    if not affordable:
        return None  # Trigger fallback

    return min(affordable, key=lambda m: m.cost.per_request)
```

### 6.4 Cost Tracking Per Query

```json
{
  "query_id": "qry_001",
  "model_selected": "sqlcoder-7b-2",
  "cost_inference": 0.0003,
  "cost_fallback_chain": 0.0,
  "cost_total": 0.0003,
  "cost_ceiling": 0.005,
  "savings_vs_gpt4o": 0.0197,
  "currency": "USD"
}
```

---

## 7. Latency-Aware Routing

### 7.1 Latency Budget Allocation

The end-to-end query latency budget includes model inference time. The router must ensure the selected model can complete within the remaining budget:

| Query Complexity | Total Budget | Non-Inference Budget | Inference Budget |
|------------------|-------------|---------------------|------------------|
| Simple | 2,500ms | 1,100ms | 1,400ms |
| Medium | 4,500ms | 1,700ms | 2,800ms |
| Complex | 8,000ms | 2,300ms | 5,700ms |

### 7.2 Latency-Aware Selection

```
function select_within_latency(capable_models, query_intent, time_remaining):
    eligible = [
        m for m in capable_models
        if m.latency.p95_ms <= time_remaining
    ]

    if not eligible:
        # Relax latency requirement — accept slower model
        eligible = sorted(
            capable_models,
            key=lambda m: m.latency.p95_ms
        )
        # Log budget overrun warning
        logger.warning("Latency budget exceeded", ...)

    return eligible
```

### 7.3 Streaming Considerations

When streaming is enabled, the router considers first-token latency instead of total latency:

| Model | First Token P50 | User Perception |
|-------|----------------|-----------------|
| SQLCoder-7b | 200ms | "Immediate" |
| Qwen2.5-72B | 500ms | "Fast" |
| DeepSeek-V3 | 1,000ms | "Reasonable" |
| GPT-4o | 300ms (API) | "Fast" |

Streaming queries may route to larger models more aggressively because the user begins seeing output sooner.

---

## 8. Complexity Estimation

### 8.1 Input

The Intent Agent computes a `ComplexityScore` with the following fields:

```json
{
  "table_count": 3,
  "join_count": 2,
  "has_subqueries": false,
  "has_cte": true,
  "has_window_functions": true,
  "has_set_operations": false,
  "has_cross_db_references": false,
  "aggregation_complexity": "group_by_with_multiple_aggregates",
  "where_complexity": "multi_condition_with_subquery",
  "semantic_ambiguity": 0.2,
  "domain": "sales",
  "overall_complexity": 0.65,
  "complexity_label": "medium"
}
```

### 8.2 Complexity Scoring Formula

```
overall_complexity = min(1.0,
    0.25 * (table_count / 10) +
    0.15 * (join_count / 5) +
    0.10 * (1 if has_subqueries else 0) +
    0.10 * (1 if has_cte else 0) +
    0.10 * (1 if has_window_functions else 0) +
    0.05 * (1 if has_set_operations else 0) +
    0.15 * (1 if has_cross_db_references else 0) +
    0.05 * aggregation_complexity_factor +
    0.05 * where_complexity_factor
)

complexity_label = (
    "simple"   if overall_complexity < 0.3
    else "medium"  if overall_complexity < 0.6
    else "complex" if overall_complexity < 0.85
    else "very_complex"
)
```

### 8.3 Complexity Buckets

| Bucket | Score Range | Expected % | Typical Model | Max Cost |
|--------|-------------|------------|---------------|----------|
| Simple | 0.00 - 0.30 | 50% | SQLCoder-7b | $0.0003 |
| Medium | 0.30 - 0.60 | 30% | Qwen2.5-72B | $0.002 |
| Complex | 0.60 - 0.85 | 15% | DeepSeek-V3 | $0.01 |
| Very Complex | 0.85 - 1.00 | 5% | GPT-4o / Claude | $0.02 |

---

## 9. Confidence Scoring

### 9.1 Purpose

Confidence scoring prevents routing to a model that is unlikely to produce a correct result for the given query type. It is the final gate before routing is confirmed.

### 9.2 Confidence Sources

| Source | Weight (MVP) | Description |
|--------|-------------|-------------|
| **Model's mean accuracy** | 0.40 | Historical accuracy of this model on similar queries |
| **Query type match** | 0.25 | How well the query type matches the model's training distribution |
| **Domain match** | 0.15 | Model performance on this domain (schema, business area) |
| **Recent drift** | 0.10 | Accuracy trend over last 24 hours (detect degradation) |
| **Similar query history** | 0.10 | Accuracy on queries similar to this one (cosine similarity) |

### 9.3 Confidence Thresholds

| Routing Action | Threshold | Behavior if Below |
|----------------|-----------|-------------------|
| Route to primary selected model | >= 0.70 | Try next model in capability-sorted list |
| Route to fallback tier 1 | >= 0.50 | Use GPT-4o mini or DeepSeek-V3 |
| Route to fallback tier 2 | >= 0.30 | Use GPT-4o (highest confidence cloud model) |
| No model confidence | < 0.30 | Return error: "Query too ambiguous — please rephrase" |

### 9.4 Confidence Calibration

Confidence scores are calibrated against actual outcomes:

- **Overconfident drift**: If model's actual accuracy < predicted confidence by > 0.10, apply penalty
- **Underconfident drift**: If model's actual accuracy > predicted confidence by > 0.10, apply bonus
- **Calibration check**: Weekly automated evaluation against test suite

---

## 10. Fallback Strategy

### 10.1 Fallback Chain

```
Primary Model
    │ (fail: invalid SQL, timeout, unhealthy)
    ▼
Next Cheapest Capable Model
    │ (fail)
    ▼
Next Strongest Model (ignore cost ceiling)
    │ (fail)
    ▼
Cloud Fallback (GPT-4o / Claude)
    │ (fail)
    ▼
Error: "Unable to process query — all models failed"
```

### 10.2 Fallback Triggers

| Trigger | Detection | Action |
|---------|-----------|--------|
| Generator returns invalid SQL | Validation agent rejects | Fallback to next model |
| Model unhealthy at routing time | Health probe failed | Skip model, fallback to next |
| Model timeout during generation | Generator timeout exception | Fallback to next model |
| Cost ceiling exceeded | Escalation budget depleted | Stop fallback chain |
| All models failed | No healthy models remain | Return error with diagnostic info |

### 10.3 Escalation Budget

| Budget | Limit | Enforced By |
|--------|-------|-------------|
| Max escalations per query | 2 | Router Fallback Executor |
| Additional cost per escalation | Varies (next tier) | Cost-aware filter |
| Max additional cost | $0.02 (total) | Cost ceiling check |
| Max additional latency | 2× primary model latency | Latency timeout |

### 10.4 Fallback Decision Flow

```
FALLBACK_ENTRY:
    attempt = 0
    escalation_cost = 0

    while attempt < MAX_ESCALATIONS:
        attempt += 1

        # Get next candidate
        candidate = get_next_capable_model(
            exclude=[previously_failed_models],
            cost_ceiling=remaining_budget
        )

        if not candidate:
            # All local models exhausted — use cloud fallback
            candidate = get_cloud_fallback()

        if not candidate:
            return ROUTING_FAILURE

        # Route to candidate
        result = route_to_model(candidate, query)

        if result.success:
            return result
        else:
            log_failure(result)
            escalation_cost += candidate.cost
            previously_failed_models.add(candidate.model_id)

    # All attempts exhausted
    return ROUTING_FAILURE
```

---

## 11. Provider Abstraction Layer

### 11.1 Purpose

The Provider Abstraction Layer decouples the routing system from the concrete mechanism of running model inference. The router selects a model; the provider abstraction handles the "how" — local GPU inference, cloud API call, or future backend.

### 11.2 Provider Interface

```python
class InferenceProvider(ABC):
    """Abstract interface for all inference providers."""

    @abstractmethod
    async def complete(
        self,
        model_id: str,
        prompt: str,
        params: InferenceParams,
        timeout_ms: int,
    ) -> InferenceResult:
        """Send a completion request to this provider's backend."""
        ...

    @abstractmethod
    async def health(self, model_id: str) -> HealthStatus:
        """Check provider health for a specific model."""
        ...

    @abstractmethod
    async def count_tokens(self, model_id: str, text: str) -> int:
        """Token count for model (models may use different tokenizers)."""
        ...

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """local, cloud, mock, or custom."""
        ...
```

### 11.3 Provider Implementations

| Provider | Type | Backend | Use Case |
|----------|------|---------|----------|
| `LocalVLLMProvider` | local | vLLM / SGLang on AMD ROCm or CUDA | Self-hosted models |
| `CloudOpenAIProvider` | cloud | OpenAI API (GPT-4o, GPT-4o-mini) | Cloud fallback |
| `CloudAnthropicProvider` | cloud | Anthropic API (Claude 3.5 Sonnet/Opus) | Cloud fallback (Enterprise) |
| `MockProvider` | mock | Configurable responses | Testing, development |
| `CacheProvider` | local | Redis-based result cache | Exact query match cache |

### 11.4 Provider Selection

The provider is determined by the model's profile:

```json
{
  "model_id": "gpt-4o",
  "provider": {
    "type": "cloud",
    "implementation": "CloudOpenAIProvider",
    "config": {
      "api_key_env": "OPENAI_API_KEY",
      "endpoint": "https://api.openai.com/v1",
      "org_id": null,
      "rate_limit_rpm": 10000,
      "max_retries": 3
    }
  }
}
```

### 11.5 Adding a New Provider

To add a new inference provider (e.g., AWS Bedrock, GCP Vertex AI, Together AI):

1. Implement the `InferenceProvider` interface
2. Register the provider in the provider factory
3. Add model profiles that reference the new provider type
4. No routing code changes needed — the router operates on capability profiles

---

## 12. Local Model Inference

### 12.1 Architecture

```
Model Router
    │
    ▼
Provider Abstraction Layer
    │
    ▼
LocalVLLMProvider
    │
    ├──► vLLM (SQLCoder-7b) ───► AMD ROCm / NVIDIA GPU
    ├──► SGLang (Qwen2.5-72B) ──► AMD ROCm / NVIDIA GPU
    └──► vLLM (DeepSeek-V3) ────► AMD ROCm / NVIDIA GPU
```

### 12.2 Local Model Pool

Each local model runs as a separate inference deployment. The router selects a model by ID and the provider routes to the correct endpoint.

| Model | Serving Framework | Endpoint | GPU Memory | Pods per GPU |
|-------|------------------|----------|------------|-------------|
| SQLCoder-7b-2 | vLLM | `http://inference-sqlcoder:8000` | 16GB | 8 |
| Qwen2.5-72B | SGLang | `http://inference-qwen:8000` | 72GB | 3 |
| DeepSeek-V3 | vLLM | `http://inference-deepseek:8000` | 128GB | 2 |
| BGE-M3 (embedding) | Sentence-Transformers | `http://inference-bge:8000` | 2GB | 16 |

### 12.3 Queue Management

Each local inference endpoint has a queue. The router checks queue depth before routing:

```
if model.queue_depth >= model.max_concurrent * 0.8:
    # Model is near capacity — warn but route anyway
    logger.warning(f"Model {model_id} near capacity")

if model.queue_depth >= model.max_concurrent:
    # Model is at capacity — skip to next capable model
    continue  # Next iteration of candidate loop
```

### 12.4 Local Model Lifecycle

| Event | Action | Routing Impact |
|-------|--------|----------------|
| Model deployment | Register in Model Registry, health check | Immediately eligible |
| Model update (new version) | Register new version, deprecate old | Gradual traffic shift |
| Model unhealthy | Automatic health check failure | Removed from routing |
| Model maintenance | Set status=maintenance | Removed from routing |
| Model scaling | Add/remove pods | Queue depth adjusts automatically |

---

## 13. Cloud Model Gateway

### 13.1 Purpose

Cloud models serve as:
1. **Fallback** when all self-hosted models fail or are unhealthy
2. **Very complex queries** requiring frontier models (GPT-4o, Claude 3.5 Opus)
3. **Enterprise customers** who explicitly request cloud models
4. **Cold-start phase** before self-hosted models are deployed

### 13.2 Cloud Provider Configuration

```json
{
  "cloud_providers": {
    "openai": {
      "enabled": true,
      "models": [
        {
          "model_id": "gpt-4o",
          "capabilities": {
            "max_complexity": 1.0,
            "supports_all_features": true,
            "dialects": "all"
          },
          "cost": {
            "per_request": 0.02,
            "per_input_token": 0.00001,
            "per_output_token": 0.00003
          },
          "latency": {
            "p50_ms": 3000,
            "p95_ms": 8000
          }
        },
        {
          "model_id": "gpt-4o-mini",
          "capabilities": {
            "max_complexity": 0.6,
            "dialects": "all"
          },
          "cost": {
            "per_request": 0.002,
            "per_input_token": 0.0000015,
            "per_output_token": 0.000006
          }
        }
      ]
    },
    "anthropic": {
      "enabled": false,
      "models": [...]
    }
  }
}
```

### 13.3 Cloud API Key Management

| Concern | Mechanism |
|---------|-----------|
| Key storage | External Secrets Operator → K8s Secrets |
| Key rotation | Automated 90-day rotation via External Secrets |
| Per-tenant keys | Enterprise tier can bring their own API keys |
| Rate limiting | Local token bucket per API key |
| Cost tracking | Separate cost ledger for cloud API usage |

### 13.4 Cloud Fallback Conditions

| Condition | Threshold | Cloud Model |
|-----------|-----------|-------------|
| All local models unhealthy | Health check failed | GPT-4o |
| Query too complex | complexity > 0.85 | GPT-4o |
| User preference | Enterprise tier config | Per-tenant preferred cloud model |
| Cold start | No local models deployed | GPT-4o-mini |

---

## 14. AMD ROCm Integration

### 14.1 Hardware Abstraction

The local inference backend abstracts AMD ROCm and NVIDIA CUDA behind a common vLLM/SGLang interface:

```python
# lib/inference/hardware.py
class GPUPlatform(Enum):
    AMD_ROCM = "rocm"
    NVIDIA_CUDA = "cuda"
    CPU = "cpu"

def detect_gpu_platform() -> GPUPlatform:
    if os.path.exists("/usr/local/cuda/bin/nvcc"):
        return GPUPlatform.NVIDIA_CUDA
    if os.path.exists("/opt/rocm/bin/rocm-smi"):
        return GPUPlatform.AMD_ROCM
    return GPUPlatform.CPU

def inference_backend_config(platform: GPUPlatform, model_id: str) -> dict:
    config = {
        "model": model_id,
        "gpu_memory_utilization": 0.90,
        "max_num_seqs": 256,
    }
    if platform == GPUPlatform.NVIDIA_CUDA:
        config["tensor_parallel_size"] = int(os.getenv("GPU_COUNT", "1"))
        config["enable_flash_attention"] = True
    elif platform == GPUPlatform.AMD_ROCM:
        config["tensor_parallel_size"] = int(os.getenv("GPU_COUNT", "1"))
        config["enable_flash_attention"] = False  # FA2 not available on ROCm
        config["dtype"] = "float16"
    return config
```

### 14.2 ROCm-Specific Configuration for Self-Hosted Models

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| ROCm version | 6.3.2 | Latest stable with vLLM/SGLang support |
| MI300X memory | 192GB HBM3 | Sufficient for DeepSeek-V3 class models |
| vLLM ROCm flags | `--dtype float16` | Best performance on AMD GPUs |
| SGLang ROCm flags | `--enable-torch-compile` | Torch compile supported on ROCm 6.3+ |
| Flash Attention | Disabled | Not available on ROCm — use sdp backend |
| Continuous batching | Enabled | vLLM handles batching natively |
| GPU MPS | Not available on MI300X | Use dedicated GPU assignment via K8s |

### 14.3 GPU Pod Scheduling

The router does not schedule GPU pods — that is handled by K8s. However, the router must be aware of GPU capacity for queue management:

```python
async def estimate_local_model_capacity(model_id: str) -> CapacityInfo:
    """Query K8s API or inference service for current capacity."""
    inference_service = f"inference-{model_id}"
    health = await http_get(f"http://{inference_service}:8000/health")

    return CapacityInfo(
        active_pods=health["active_pods"],
        max_pods=health["desired_pods"],
        queue_depth=health["queue_depth"],
        avg_gpu_utilization=health["gpu_utilization"],
    )
```

### 14.4 Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Flash Attention 2 unavailable | ~15% slower prefill | Over-provision by 15%, plan FA2 port |
| vLLM prefill ~10% slower on ROCm | Higher P99 first-token latency | Additional GPU buffer (15% over-provision) |
| No CUDA Graphs | Higher per-request overhead | Use continuous batching |
| Tensor parallelism scaling | Less efficient than NCCL on CUDA | Use pipeline parallelism as alternative |

---

## 15. NVIDIA Compatibility

### 15.1 Dual-Platform Strategy

| Phase | Timeline | GPU Support | Router Impact |
|-------|----------|-------------|--------------|
| 1 (MVP) | Now | **AMD ROCm only** (MI300X) | All local models → ROCm backend |
| 2 | Y2 Q1 | Add NVIDIA support | Router adds `gpu_platform` to model profile selection |
| 3 | Y2 Q3 | Auto-detect GPU platform | Router selects backend based on node label |
| 4 | Y3 | Mixed GPU pool (AMD + NVIDIA) | Router selects best GPU for model + availability |

### 15.2 Model Profile for NVIDIA

Models can declare platform compatibility:

```json
{
  "model_id": "sqlcoder-7b-2",
  "provider": {
    "type": "local",
    "platform_compatibility": ["rocm", "cuda"],
    "endpoints": {
      "rocm": "http://inference-sqlcoder-rocm:8000",
      "cuda": "http://inference-sqlcoder-cuda:8000"
    }
  }
}
```

### 15.3 Router Selection with Mixed GPU Pool

When both AMD ROCm and NVIDIA GPU nodes serve the same model, the router selects based on:

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Queue depth | 0.4 | Route to GPU pool with shorter queue |
| Platform preference | 0.3 | Enterprise config — some customers prefer NVIDIA |
| Cost per request | 0.2 | Different GPU SKUs have different amortized costs |
| Previous failures | 0.1 | Avoid platform with recent errors |

---

## 16. Routing API

### 16.1 Endpoints

#### `POST /v1/route`

Select a model for a query.

**Request**:
```json
{
  "query_id": "qry_001",
  "tenant_id": "tnt_001",
  "user_tier": "pro",
  "query_intent": {
    "type": "aggregate",
    "domain": "sales",
    "dialect": "postgresql",
    "table_count": 3,
    "join_count": 2,
    "has_subqueries": false,
    "has_cte": true,
    "has_window_functions": false,
    "has_set_operations": false,
    "has_cross_db_references": false,
    "aggregation_complexity": "group_by_with_sum",
    "where_complexity": "multi_condition",
    "semantic_ambiguity": 0.1,
    "overall_complexity": 0.55,
    "complexity_label": "medium"
  },
  "constraints": {
    "max_cost_usd": 0.02,
    "max_latency_ms": 5000,
    "preferred_provider": null,
    "requires_streaming": true,
    "cost_ceiling_source": "tenant_tier"
  }
}
```

**Response**:
```json
{
  "query_id": "qry_001",
  "selection": {
    "model_id": "qwen2.5-72b",
    "model_name": "Qwen2.5-72B-Instruct",
    "provider": {
      "type": "local",
      "endpoint": "http://inference-qwen:8000/v1/completions",
      "backend": "sglang"
    },
    "estimated_cost": 0.002,
    "estimated_latency_ms": 1500,
    "estimated_first_token_ms": 500,
    "confidence": 0.88
  },
  "alternatives": [
    {
      "model_id": "deepseek-v3",
      "cost": 0.01,
      "latency_ms": 3000,
      "confidence": 0.92,
      "reason_not_selected": "Cost 5x higher than primary, sufficient confidence on primary"
    }
  ],
  "routing_rationale": {
    "strategy": "rules",
    "matching_models": 3,
    "capability_match": true,
    "cost_filter": "qwen2.5-72b cheapest capable",
    "latency_filter": "within budget",
    "confidence_gate": "passed (0.88 >= 0.75)",
    "tenant_policy": "pro tier: standard routing"
  },
  "fallback_plan": {
    "chain": ["deepseek-v3", "gpt-4o"],
    "max_escalations": 2,
    "budget_remaining": 0.018
  },
  "timing_ms": {
    "routing_decision": 3,
    "registry_lookup": 1,
    "strategy_evaluation": 2
  }
}
```

#### `GET /v1/models`

List all registered models.

**Response**:
```json
{
  "models": [
    {
      "model_id": "sqlcoder-7b-2",
      "name": "SQLCoder-7B-v2",
      "status": "healthy",
      "capability_summary": "simple: select, filter, aggregate (≤2 tables)",
      "cost_per_request": 0.0003,
      "p50_latency_ms": 800,
      "queue_depth": 3
    },
    {
      "model_id": "qwen2.5-72b",
      "name": "Qwen2.5-72B-Instruct",
      "status": "healthy",
      "capability_summary": "medium: join, group_by, subqueries (≤4 tables)",
      "cost_per_request": 0.002,
      "p50_latency_ms": 1500,
      "queue_depth": 5
    }
  ],
  "total_count": 5
}
```

#### `POST /v1/route/explain`

Get a detailed explanation of why a query would be routed to a particular model, without actually executing the routing.

**Request**: Same as `POST /v1/route`

**Response**: Same as `POST /v1/route` but with additional `simulation` field showing what-if scenarios:

```json
{
  "simulation": {
    "what_if": [
      {
        "scenario": "switch to gpt-4o-mini",
        "cost": 0.002,
        "latency_ms": 1200,
        "confidence": 0.82,
        "recommended": false,
        "reason": "Lower confidence than primary (0.82 vs 0.88)"
      },
      {
        "scenario": "remove cost ceiling",
        "selected_model": "deepseek-v3",
        "cost": 0.01,
        "latency_ms": 3000,
        "confidence": 0.95,
        "recommended": false,
        "reason": "Higher cost without meaningful accuracy gain for this query type"
      }
    ]
  }
}
```

### 16.2 Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `ROUTING_SUCCESS` | 200 | Model selected successfully |
| `ROUTING_NO_CAPABLE_MODEL` | 200 (with warning) | No model meets capability requirements — routing to strongest available |
| `ROUTING_ALL_UNHEALTHY` | 503 | All models unhealthy |
| `ROUTING_COST_CEILING_EXCEEDED` | 402 | Query cost exceeds ceiling and no alternatives |
| `ROUTING_INVALID_INTENT` | 400 | QueryIntent is malformed or incomplete |
| `ROUTING_INTERNAL_ERROR` | 500 | Unexpected routing failure |

### 16.3 Timeouts

| Operation | Timeout | Behavior |
|-----------|---------|----------|
| Routing decision | 50ms | Return strongest model (circuit breaker) |
| Model registry lookup | 10ms | Use cached profiles |
| Provider health check | 5s | Assume unhealthy, skip to next |
| Total routing call | 100ms | Fail open to strongest model |

---

## 17. Cache Strategy

### 17.1 Routing Decision Cache

Identical routing requests should not be re-evaluated:

```json
{
  "cache_key": "hash(tenant_id + intent_type + complexity_label + dialect)",
  "ttl_seconds": 300,
  "store": "Redis",
  "hit_ratio_target": 0.30
}
```

### 17.2 Cache Invalidation

| Event | Action |
|-------|--------|
| Model health change | Invalidate affected routing decisions |
| Model cost update | Invalidate all (cost profiles changed) |
| New model registered | Invalidate all (new capabilities available) |
| Tenant tier change | Invalidate per-tenant cache |

---

## 18. Metrics and Monitoring

### 18.1 Routing Metrics

| Metric | Type | Labels | Target |
|--------|------|--------|--------|
| `router.decision_latency_ms` | Histogram | strategy, complexity | P50 < 3ms, P99 < 10ms |
| `router.decisions_total` | Counter | model_id, intent_type, tenant_tier | Track volume |
| `router.cost_per_query` | Histogram | model_id, tenant_tier | Mean < $0.005 |
| `router.savings_vs_gpt4o` | Counter | tenant_tier | Track savings |
| `router.fallback_chain_length` | Histogram | — | Mean < 0.1 |
| `router.fallback_rate` | Counter | trigger_reason | < 5% |
| `router.no_capable_model` | Counter | — | < 1% |
| `router.cache_hit_ratio` | Gauge | — | > 30% |
| `router.model_health_status` | Gauge | model_id | 1 = healthy |
| `router.routing_accuracy` | Gauge (drift) | model_id | > 85% |

### 18.2 Model Performance Metrics

| Metric | Type | Source | Target |
|--------|------|--------|--------|
| `model.inference_latency_ms` | Histogram | Provider | Per-model P50/P95/P99 budgets |
| `model.first_token_latency_ms` | Histogram | Provider | Per-model budgets |
| `model.queue_depth` | Gauge | Inference service | < max_concurrent |
| `model.gpu_utilization` | Gauge | ROCm/CUDA exporter | > 70% |
| `model.error_rate` | Counter | Provider | < 2% |
| `model.invalid_sql_rate` | Counter | Validator | Per-model tracking |
| `model.accuracy` | Gauge (drift) | Learning Agent | Per-model trend |

### 18.3 Dashboards

| Dashboard | Audience | Key Charts |
|-----------|----------|------------|
| **Routing Overview** | Ops | Decision latency, cost/query, model distribution, fallback rate |
| **Model Health** | ML Ops | Health status per model, queue depth, GPU utilization, error rates |
| **Cost Dashboard** | Finance | Daily inference cost, savings vs API, cost per tenant tier |
| **Quality Dashboard** | Engineering | Model accuracy drift, invalid SQL rate, fallback chain distribution |

### 18.4 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| Fallback rate spike | Fallback rate > 10% in 5 min | Warning |
| All local models unhealthy | No healthy local model | Critical |
| Cost ceiling breach | Daily cost > 120% of budget | Warning |
| Router latency spike | P99 routing > 50ms | Warning |
| Model accuracy drop | Model accuracy drops > 5% in 24h | Warning |

---

## 19. Testing Strategy

### 19.1 Unit Tests

| Test | What It Verifies |
|------|------------------|
| Capability matching | Given a query intent, correct models are identified as capable |
| Cost ceiling filter | Models above cost ceiling are excluded |
| Latency filter | Models above latency budget are deprioritized |
| Confidence gate | Models below confidence threshold are skipped |
| Fallback chain | Correct fallback sequence when primary fails |
| Provider selection | Correct provider backend is selected for model |
| Cache hit/miss | Cached routing decisions are returned correctly |
| Edge: empty registry | Behavior when no models registered |
| Edge: all unhealthy | Behavior when all models unhealthy |

### 19.2 Integration Tests

| Test | What It Verifies |
|------|------------------|
| Registry CRUD | Add, update, delete models through registry API |
| Router ↔ Registry | Router correctly reads model profiles |
| Router ↔ Provider | Router correctly routes inference call |
| Router ↔ Health | Router respects health status |
| Mock provider | Mock provider returns configurable results for deterministic testing |
| End-to-end routing | Full flow: Intent → Router → Generator → Validation |

### 19.3 Routing Accuracy Tests

Test that the router selects the correct model for different query types:

```python
ROUTING_TEST_CASES = [
    # (name, intent, expected_tier, acceptable_tiers)
    RoutingTestCase(
        name="simple_select_one_table",
        intent=QueryIntent(type="select", table_count=1, join_count=0,
                           complexity=0.1, dialect="postgresql"),
        expected_tier="simple",
        acceptable_tiers=["simple"],
    ),
    RoutingTestCase(
        name="medium_join_two_tables",
        intent=QueryIntent(type="aggregate", table_count=3, join_count=2,
                           complexity=0.5, has_cte=True, dialect="postgresql"),
        expected_tier="medium",
        acceptable_tiers=["medium", "complex"],
    ),
    RoutingTestCase(
        name="complex_window_cte",
        intent=QueryIntent(type="analytical", table_count=6, join_count=3,
                           complexity=0.75, has_cte=True, has_window_functions=True,
                           dialect="postgresql"),
        expected_tier="complex",
        acceptable_tiers=["complex", "very_complex"],
    ),
    RoutingTestCase(
        name="cross_db_federated",
        intent=QueryIntent(type="join", table_count=4, join_count=3,
                           complexity=0.9, has_cross_db_references=True,
                           dialect="postgresql"),
        expected_tier="very_complex",
        acceptable_tiers=["very_complex"],
    ),
    RoutingTestCase(
        name="tenant_cost_ceiling_starter",
        intent=QueryIntent(type="aggregate", table_count=5, join_count=3,
                           complexity=0.6, dialect="postgresql"),
        tenant_tier="starter",
        expected_cost_max=0.005,
        acceptable_tiers=["medium"],
    ),
]
```

### 19.4 Performance Tests

| Test | Target | Method |
|------|--------|--------|
| Routing latency under load | P99 < 10ms at 1000 req/s | k6 load test against router endpoint |
| Registry cache hit ratio | > 90% after warmup | Test with repeated query intents |
| Concurrent routing accuracy | No race conditions in model selection | 50 concurrent routing requests |
| Cold start latency (no cache) | P99 < 30ms | First request after cache flush |

### 19.5 Chaos Tests

| Test | Scenario | Expected Behavior |
|------|----------|-------------------|
| All local models unhealthy | Kill all inference pods | Router routes to cloud fallback |
| Registry unavailable | Kill PostgreSQL + Redis | Router uses in-memory cache (stale up to 60s) |
| Cloud API rate limited | Mock API rate limit error | Router returns to local models |
| High latency from model | Inject 10s delay on inference | Router escalates to next capable model |
| Corrupt model profile | Register invalid capability profile | Router validation rejects, logs error |

---

## 20. Failure Handling

### 20.1 Failure Modes

| Failure | Detection | Recovery | User Impact |
|---------|-----------|----------|-------------|
| All local models unhealthy | Health probes fail | Route to cloud fallback | Higher cost, potential latency increase |
| Cloud API unavailable | API returns 5xx/429 | Route to strongest local model | Possible accuracy degradation |
| Registry unavailable | PostgreSQL + Redis down | Use in-memory cache (stale up to 60s) | No impact (stale profiles) |
| Router service down | K8s liveness probe | K8s restarts pod | Pipeline retries routing (idempotent) |
| Corrupted model profile | Validation error | Skip corrupted model, log error | Might miss optimal model |
| Intent classification wrong | Downstream validation fails | Fallback to next model tier | Additional cost, latency |
| Cost ceiling exceeded | No model fits budget | Route to cheapest available, log warning | Higher cost than expected |

### 20.2 Circuit Breaker

If a model consistently fails, the router applies a circuit breaker:

```
CLOSED (normal)
    │
    │ Error rate > 10% in 5 min
    ▼
OPEN (skip model)
    │
    │ 30-second cooldown
    ▼
HALF_OPEN (test one request)
    │
    ├── Success → CLOSED
    └── Fail → OPEN (reset cooldown to 60s, max 300s)
```

### 20.3 Degraded Behavior

| Scenario | Degraded Mode | Recovery |
|----------|--------------|----------|
| Router timeout (> 50ms) | Route to strongest available model | Next request uses cache or fresh eval |
| Partial health data | Assume healthy if data missing | Normal routing after health data restored |
| Cost data missing | Assume median cost for model class | Normal routing after cost data restored |
| Registry sync failure | Use 60-second stale cache | Normal routing after sync restored |

---

## 21. Security Considerations

### 21.1 Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Model registry poisoning | Attacker registers malicious model | Registry mutations require admin auth. All model profiles validated against schema. Signatures verified. |
| Cost ceiling bypass | Attacker sends complex queries to cheap model | Cost ceiling enforced at router. Validated against tenant tier on every route. |
| Cloud API key leak | Unauthorized API usage | Keys stored in External Secrets. Separate keys per tenant for Enterprise. |
| Router DoS | Excessive routing calls overwhelm service | Rate limit per tenant. Router stateless (can scale horizontally). |
| Model health probe spoofing | Fake healthy/unhealthy status | Health probes authenticated via mTLS. Inference endpoints on internal network. |

### 21.2 Tenant Isolation

| Mechanism | Scope | Enforced At |
|-----------|-------|-------------|
| Cost ceiling per tenant | Query-level | Router |
| Model availability per tenant | Registry-level | Router reads tenant preferences |
| API key isolation | Provider-level | Cloud gateway uses tenant-specific keys |
| Audit log | Decision-level | All routing decisions logged with tenant_id |

---

## 22. Future Improvements

### 22.1 Short-Term (Phase 2 — Y2 Q1)

| Improvement | Effort | Benefit |
|-------------|--------|---------|
| Learned routing (ML classifier replaces rules) | 3-4 weeks | +5-10% routing accuracy, adapts to query distribution |
| Dynamic cost modeling (actual GPU cost per query) | 1-2 weeks | More accurate cost tracking, better routing decisions |
| Tenant routing policies (UI-configurable overrides) | 2 weeks | Enterprise customers can customize model selection |
| Multi-model ensemble for critical queries | 2-3 weeks | Improved accuracy for high-stakes Enterprise queries |

### 22.2 Medium-Term (Phase 3 — Y2 Q3)

| Improvement | Effort | Benefit |
|-------------|--------|---------|
| A/B model comparison (route same query to 2 models, compare) | 4-6 weeks | Empirical accuracy measurement, continuous optimization |
| Query-specific fine-tuning feedback loop | 6-8 weeks | Router triggers fine-tuning when accuracy drops |
| NVIDIA GPU support in routing | 2-3 weeks | Hardware vendor flexibility, cost optimization |
| Predictive routing (pre-warm model based on user pattern) | 3-4 weeks | Reduce cold-start latency for expected queries |

### 22.3 Long-Term (Year 3+)

| Improvement | Effort | Benefit |
|-------------|--------|---------|
| Cross-tenant routing optimization (pool capacity) | 8-12 weeks | Global cost optimization across tenants |
| Automatic model retirement (detect obsolete models) | 4-6 weeks | Reduce maintenance burden |
| Cost anomaly detection (ML-based cost monitoring) | 4-6 weeks | Early detection of cost regressions |
| Multi-objective routing optimization (Pareto frontier) | 8-12 weeks | Optimal cost-latency-accuracy trade-off for each query |

---

## References

| Source | Relevance |
|--------|-----------|
| [ADR-008 Tiered Model Routing](../decisions/ADR-008-Tiered-Model-Routing.md) | Architectural basis for tiered routing |
| [ADR-009 Self-Hosted Inference Primary](../decisions/ADR-009-Self-Hosted-Inference-Primary.md) | Local vs cloud model strategy |
| [Performance-Specification.md](Performance-Specification.md) §5 | Current simple router — this spec supersedes it |
| [AI-Agent-Specification.md](AI-Agent-Specification.md) §2 | Intent Agent provides routing inputs |
| [Infrastructure-Specification.md](Infrastructure-Specification.md) §17-19 | GPU scheduling, ROCm, NVIDIA configuration |
| [KnowledgeEngine-Specification.md](KnowledgeEngine-Specification.md) §9 | Metrics storage for routing decisions |
| [Database-Specification.md](Database-Specification.md) | Model registry storage schema |
| [System-Architecture.md](../System-Architecture.md) §3 | Component positioning in architecture |
| [Architecture-Review.md](../Architecture-Review.md) §10.8-10.9 | ADR review and validation |
