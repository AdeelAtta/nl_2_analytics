# Data Flow

**Enterprise Data Intelligence Platform — Phase 2 Architecture & Design**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [System-Architecture.md](./System-Architecture.md), [Knowledge-Engine.md](./Knowledge-Engine.md), [Component-Design.md](./Component-Design.md), [API-Design.md](./API-Design.md) |

---

## 1. Flow Overview

The platform has three primary data flows:

| Flow | Direction | Latency Sensitivity | Frequency |
|------|-----------|-------------------|-----------|
| **Query Flow** | User → Knowledge Engine → Pipeline → Database → User | High (sub-second to seconds) | Per user request |
| **Ingestion Flow** | Database → Schema Intelligence → Knowledge Engine | Medium (minutes) | Per DB connection + daily refresh |
| **Learning Flow** | User Feedback → Collector → Learning Loop → Knowledge Engine | Low (minutes to hours) | Continuous (batched) |

---

## 2. Query Flow (Read Path)

### 2.1 Overview

```
User ──► API Layer ──► Query Pipeline ──► Guardrails ──► Executor ──► Database ──► User
                            │                   │             │
                            ▼                   ▼             ▼
                      Knowledge Engine     Knowledge     Knowledge
                      (retrieve context)   Engine        Engine
                                           (check        (log query
                                            policies)     + result)
```

### 2.2 Step-by-Step

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│  User  │────►│  API   │────►│ Query  │────►│Context │────►│ Query  │
│        │     │ Layer  │     │Analyzer│     │Retriever│     │Planner │
└────────┘     └────────┘     └────────┘     └────────┘     └────────┘
                                                                    │
                         ┌────────┐     ┌────────┐     ┌────────┐  │
                         │ Result │◄────│Executor│◄────│Guards  │◄─┘
                         │        │     │        │     │ Stack  │
                         └────────┘     └────────┘     └────────┘
                              │              │
                              ▼              ▼
                         ┌────────┐     ┌────────┐
                         │  User  │     │Knowledge│
                         │        │     │ Engine  │
                         └────────┘     └────────┘
```

### 2.3 Detailed Sequence

```
User                API Layer           Query Analyzer      Context Retriever
 │                     │                     │                     │
 │  POST /v1/query     │                     │                     │
 │  {"question":       │                     │                     │
 │   "show me revenue  │                     │                     │
 │    by month"}       │                     │                     │
 │────────────────────►│                     │                     │
 │                     │  1. Auth + tenant   │                     │
 │                     │  2. Rate limit      │                     │
 │                     │  3. Validate input  │                     │
 │                     │────────────────────►│                     │
 │                     │                     │  4. Extract entities │
 │                     │                     │     intent, filters  │
 │                     │                     │                     │
 │                     │                     │  resolve(user,      │
 │                     │                     │   tenant)           │
 │                     │                     │────────────────────►│
 │                     │                     │                     │
 │                     │                     │        retrieve(    │
 │                     │                     │         query_embed,│
 │                     │                     │         {top_k: 15, │
 │                     │                     │          stores:    │
 │                     │                     │          [schema,   │
 │                     │                     │           qa_pairs]})│
 │                     │                     │                     │
 │                     │                     │  context + schema   │
 │                     │                     │◄────────────────────│
 │                     │                     │                     │
 │                     │                     │                     │
Query Planner          NL2SQL Generator      Guardrail Stack       Executor
 │                     │                     │                     │
 │  context + entities │                     │                     │
 │◄────────────────────│                     │                     │
 │                     │                     │                     │
 │  resolve("revenue", │                     │                     │
 │   {tenant, db})     │                     │                     │
 │────────────────────►│                     │                     │
 │                     │ (Knowledge Engine)  │                     │
 │◄────────────────────│                     │                     │
 │  term → columns     │                     │                     │
 │                     │                     │                     │
 │  plan: {            │                     │                     │
 │   tables: [...]     │                     │                     │
 │   joins: [...]      │                     │                     │
 │   metrics: [...]}   │                     │                     │
 │────────────────────►│                     │                     │
 │                     │                     │                     │
 │                     │  generate_sql(      │                     │
 │                     │   query +           │                     │
 │                     │   context +         │                     │
 │                     │   plan)             │                     │
 │                     │                     │                     │
 │                     │  3 candidates       │                     │
 │                     │  (tiered routing)   │                     │
 │                     │  select best        │                     │
 │                     │                     │                     │
 │                     │  reflection loop    │                     │
 │                     │  (if needed)        │                     │
 │                     │                     │                     │
 │                     │  SQL + explanation  │                     │
 │                     │────────────────────►│                     │
 │                     │                     │                     │
 │                     │                     │  check: intent      │
 │                     │                     │  check: sanitize    │
 │                     │                     │  check: RBAC        │
 │                     │                     │  check: cost        │
 │                     │                     │  check: validate    │
 │                     │                     │  check: read-only   │
 │                     │                     │  check: audit       │
 │                     │                     │                     │
 │                     │                     │  execution_id       │
 │                     │                     │────────────────────►│
 │                     │                     │                     │
 │                     │                     │                     │  connect
 │                     │                     │                     │  execute SQL
 │                     │                     │                     │  fetch results
 │                     │                     │                     │
 │                     │                     │                     │  store(query_log)
 │                     │                     │                     │  store(audit)
 │                     │                     │                     │
 │                     │                     │  result + metadata  │
 │                     │                     │◄────────────────────│
 │                     │                     │                     │
 │  response: {        │                     │                     │
 │   sql, rows,        │                     │                     │
 │   explanation,      │                     │                     │
 │   execution_time,   │                     │                     │
 │   query_id}         │                     │                     │
 │◄────────────────────│                     │                     │
 │                     │                     │                     │
◄──────────────────────│                     │                     │
│
│  Render result
│  Show SQL toggle
│  Feedback prompt
│
```

### 2.4 Timing Budget

| Step | Component | Max Time | Cumulative |
|------|-----------|----------|------------|
| 1-3 | API Layer | 50ms | 50ms |
| 4 | Query Analyzer | 500ms | 550ms |
| 5-6 | Context Retriever | 150ms | 700ms |
| 7-8 | Query Planner | 300ms | 1,000ms |
| 9-11 | NL2SQL Generator | 2,000ms | 3,000ms |
| 12-18 | Guardrail Stack | 150ms | 3,150ms |
| 19-23 | Executor | 5,000ms | 8,150ms |
| 24-25 | Response | 50ms | 8,200ms |
| **Total P95** | | | **<8.5s** |
| **Total P50** | | | **<3s** |

### 2.5 Error Flows

| Failure Point | Behavior | User Experience |
|--------------|----------|-----------------|
| Context Retriever returns empty | Fall back to basic schema; no Q&A examples | Query works but less accurate |
| Query Planner fails (no join path) | Return error with "I don't know how to connect these tables" | Clear explanation, suggest alternative |
| NL2SQL Generator all 3 candidates fail | Fallback to GPT-4o/Claude | Slightly slower, higher quality |
| Guardrail blocks query | Return explanation + suggestion | Helpful message, not error |
| Executor times out (>60s) | Return partial results if available | Timeout message + partial data |
| Database unreachable | Return error with connection status | "Database 'X' is currently unreachable" |

---

## 3. Ingestion Flow (Write Path)

### 3.1 Overview

```
Database ──► Connector ──► Schema Intelligence ──► Knowledge Engine
                                                        │
                                                   ┌────┴────┐
                                                   ▼         ▼
                                              Schema Store  Vector Index
                                              + Knowledge   + QA Pairs
                                              Graph
```

### 3.2 First-Time Ingestion

```
User connects database
         │
         ▼
Trigger full introspection
         │
         ▼
┌──────────────────────────────────────────────┐
│ 1. Connector: introspect all schemas/tables   │
│    - Extract DDL, FK constraints, indexes    │  <3 min for 100 tables
│    - Extract sample values (5 per column)    │
│    - Extract row counts                      │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 2. DDL Parser: normalize schema metadata      │
│    - Canonical type names                     │
│    - Build table/column objects               │  <5s
│    - Detect explicit FKs                      │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 3. Diff Engine: compare to existing state      │
│    (first time: all new)                      │  <1s
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 4. Schema Store: write raw schema metadata     │
│    - tables, columns, relationships rows      │  <5s
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 5. Name Annotator: LLM descriptions           │
│    - Generate business_name, description      │  <120s for 100 tables
│    - Flag PII, assign tags                    │  (parallel LLM calls)
│    - Self-report confidence                   │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 6. Relationship Inferer: detect relationships │  <30s
│    - Naming patterns                          │
│    - Query history mining (if available)      │
│    - LLM inference (fallback)                 │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 7. Embedder: generate vector embeddings       │
│    - Each column: name + description          │  <10s
│    - Each table: name + description           │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 8. Graph Builder: link business terms         │
│    - Scan column names + descriptions         │  <30s
│    - Match known business terms               │
│    - Generate term-column mappings            │
└──────────────────┬───────────────────────────┘
                   ▼
         Ingestion complete
         Knowledge Engine ready
         Total: ~5 min for 100 tables
```

### 3.3 Incremental Refresh

```
Scheduled trigger (daily) or manual trigger
         │
         ▼
┌──────────────────────────────────────────────┐
│ 1. Connector: fast check                     │
│    - Compare table list checksums            │  <10s
│    - Identify new/modified/removed tables    │
└──────────────────┬───────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
     Changes found      No changes
         │                   │
         ▼                   ▼
   Full pipeline       Skip; update
   for changed         last_introspected_at
   tables only
```

### 3.4 Business Term Ingestion

```
Documentation source ──► Document Ingester
(confluence, README,         │
wiki, BI tool docs)          ▼
                        Chunk & Embed
                              │
                              ▼
                        Knowledge Engine
                        (doc_chunk_embeddings)
                              │
                              ▼
                        LLM: extract business terms
                              │
                              ▼
                        Knowledge Graph
                        (business_terms + mappings)
```

---

## 4. Learning Flow (Feedback Path)

### 4.1 Overview

```
User ──► Feedback Collector ──► Feedback Store ──► Learning Loop ──► Knowledge Engine
                                                                         │
                                                                    ┌────┴────┐
                                                                    ▼         ▼
                                                               Vector Index  Schema
                                                                             Store
```

### 4.2 Feedback Collection

```
Query result displayed to user
         │
         ▼
User action:
   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │ Thumbs up │   │ Thumbs    │   │ Edit SQL  │
   │ (approve) │   │ down      │   │ (correct) │
   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
         │               │               │
         ▼               ▼               ▼
   store("feedback", {type: "approval",
         query_id, rating: 1})
         │               │               │
         ▼               ▼               ▼
   ┌───────────────────────────────────────────┐
   │ Feedback Store (PostgreSQL)               │
   │ - query_id, user_id, type, data, created  │
   └───────────────────────────────────────────┘
```

### 4.3 Learning Loop Processing

```
Every 5 minutes (batch)
         │
         ▼
┌──────────────────────────────────────────────┐
│ 1. Feedback Collector:                       │
│    - Query unprocessed feedback              │  <1s
│    - Load associated query_logs              │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 2. Feedback Validator:                        │
│    - Check SQL validity                      │  <10s per 100 items
│    - Check meaningful difference             │
│    - Check user reliability                  │
│    - Reject spam / low-effort                │
└──────────────────┬───────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    Valid feedback       Rejected feedback
         │                   │
         ▼                   ▼
┌──────────────────┐   ┌──────────────────┐
│ 3. Q&A Builder   │   │ Flag for review  │
│    - NL + SQL    │   │ (if concerning   │
│    - Embed       │   │  pattern)        │
│    - Store in    │   └──────────────────┘
│      vector idx  │
└──────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ 4. Schema Enricher (if applicable):           │
│    - Same correction 3+ users → update desc  │  <30s
│    - Same pattern 5+ times → update business  │
│      name / confidence                       │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 5. Prompt Optimizer (if applicable):          │
│    - Maintain top-20 few-shot examples        │  <10s
│    - Per-tenant prompt configuration          │
│    - Update Knowledge Engine config store     │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ 6. Pattern Miner (nightly):                   │
│    - Template extraction from query history   │  <5min
│    - Popular join path discovery              │
│    - Implicit relationship generation         │
│    - Write to knowledge graph                 │
└──────────────────┬───────────────────────────┘
                   ▼
        Learning cycle complete
```

### 4.4 Cold Start Learning

For new tenants with zero feedback:

| Strategy | Description | Time to Effect |
|----------|-------------|----------------|
| **Synthetic Q&A** | Generate Q&A pairs from DDL + international SQL benchmarks (Spider, BIRD) | Day 1 |
| **Public SQL corpus** | Seed with anonymized, high-quality Q&A from open-source SQL datasets | Day 1 |
| **Cross-tenant patterns** | (Phase 2) Aggregate successful patterns across tenants (no raw data sharing) | Month 3 |
| **Human-in-loop curation** | Admin approves high-value Q&A pairs for their tenant | Ongoing |

---

## 5. Cross-Database Query Flow (Phase 3)

### 5.1 Overview

```
User ──► "Show me revenue from Snowflake and customers from Postgres"
         │
         ▼
Query Planner detects cross-database intent
         │
         ▼
Decompose into 2 sub-queries:
   Sub-query 1: revenue by customer_id (Snowflake)
   Sub-query 2: customer_name by customer_id (Postgres)  
         │
         ▼
Execute both queries independently
         │
         ▼
Merge results by customer_id (in-memory)
         │
         ▼
Return unified result set
```

### 5.2 Data Flow

```
         ┌──────────────────────────────────────────┐
         │            Query Planner                  │
         │  Cross-DB decomposition                   │
         └────┬─────────────────────┬────────────────┘
              │                     │
              ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ Sub-query 1     │   │ Sub-query 2     │
    │ (Snowflake)     │   │ (PostgreSQL)    │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ Query Pipeline  │   │ Query Pipeline  │
    │ (analyze,       │   │ (analyze,       │
    │  retrieve,      │   │  retrieve,      │
    │  plan, generate,│   │  plan, generate,│
    │  guard, execute)│   │  guard, execute)│
    └────────┬────────┘   └────────┬────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ Result 1        │   │ Result 2        │
    │ (customer_id,   │   │ (customer_id,   │
    │  revenue)       │   │  name)          │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             └────────┬────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Merge Engine    │
             │ JOIN by         │
             │ customer_id     │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Unified result  │
             │ (customer_id,   │
             │  name, revenue) │
             └─────────────────┘
```

---

## 6. Streaming Query Flow (Phase 2)

### 6.1 Use Case

For long-running or exploratory queries, stream results progressively:

```
User ──► POST /v1/query/stream
         │
         ▼
    [SSE Event 1] "Query received, analyzing..."
    [SSE Event 2] "Context retrieved (3 tables, 12 columns)..."
    [SSE Event 3] "Generating SQL..."
    [SSE Event 4] "SQL generated: SELECT ..."
    [SSE Event 5] "Guardrail check: intent ✅, RBAC ✅, cost ✅"
    [SSE Event 6] "Executing on Snowflake..."
    [SSE Event 7] "Rows 1-100: {data}"
    [SSE Event 8] "Rows 101-200: {data}"
    ...
    [SSE Event N] "Complete: 1,234 rows in 4.2s"
```

### 6.2 Technology

Server-Sent Events (SSE) over HTTPS. Simpler than WebSocket for one-way streaming. Universal browser support.

---

## 7. Bulk Export Flow

### 7.1 Use Case

Schedule a query to run and export results to cloud storage (S3, GCS, Snowflake stage):

```
User ──► "Run this query daily and export to S3"
         │
         ▼
    Scheduled job (Dagster/Airflow)
         │
         ▼
    Execute query
         │
         ▼
    Format results (Parquet preferred)
         │
         ▼
    Upload to destination
         │
         ▼
    Log execution in Knowledge Engine
```

---

## 8. Flow Dependencies

```
Query Flow ──► Knowledge Engine (read)
     │               │
     │               └── Requires Ingestion Flow (write) to have completed first
     │
     ▼
Feedback ──► Learning Flow (write)
                 │
                 ▼
            Knowledge Engine (updated)
                 │
                 └── Improves future Query Flows
```

**Dependency**: Query Flow depends on Ingestion Flow (can't query what hasn't been discovered). Learning Flow depends on Query Flow (can't learn from queries that haven't been executed).

---

## 9. References

| Source | Relevance |
|--------|-----------|
| [System-Architecture.md](./System-Architecture.md) | Component architecture these flows execute on |
| [Component-Design.md](./Component-Design.md) | Detailed component behavior within each flow |
| [Knowledge-Engine.md](./Knowledge-Engine.md) | Data stores each flow reads/writes |
| [API-Design.md](./API-Design.md) | API endpoints that trigger these flows |
