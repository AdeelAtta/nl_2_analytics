# Performance Budgets

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

---

## 1. Query Pipeline End-to-End Latency

| Segment | P50 (ms) | P95 (ms) | P99 (ms) | Budget Owner |
|---------|----------|----------|----------|-------------|
| API overhead (auth + rate limit) | 10 | 30 | 50 | API |
| Intent classification | 100 | 200 | 400 | Intent Agent |
| Context retrieval | 160 | 370 | 750 | Retriever |
| Query planning | 400 | 800 | 1,600 | Planner |
| SQL generation (simple) | 800 | 1,200 | 2,000 | Generator (SQLCoder) |
| SQL generation (medium) | 1,500 | 3,000 | 5,000 | Generator (Qwen2.5) |
| SQL generation (complex) | 3,000 | 5,000 | 8,000 | Generator (DeepSeek) |
| Validation + repair | 300 | 500 | 800 | Validator |
| Policy enforcement (10 layers) | 150 | 300 | 450 | Policy Enforcement |
| DB execution | 200 | 2,000 | 10,000 | Target DB |
| Result formatting | 20 | 50 | 100 | Executor |
| **Total simple query** | **~2,140** | **~4,450** | **~6,150** | — |
| **Total medium query** | **~2,840** | **~6,250** | **~10,450** | — |
| **Total complex query** | **~4,340** | **~8,250** | **~13,450** | — |

## 2. Knowledge Engine API Latency

| Operation | P50 (ms) | P95 (ms) | P99 (ms) |
|-----------|----------|----------|----------|
| Schema: read single table | 5 | 15 | 30 |
| Schema: read all tables for DB | 15 | 30 | 60 |
| Schema: upsert schema (100 tables) | 200 | 400 | 800 |
| Vector: search (top 20) | 30 | 80 | 150 |
| Vector: upsert (10 points) | 20 | 40 | 80 |
| Graph: create node | 5 | 10 | 20 |
| Graph: create edge | 5 | 10 | 20 |
| Graph: traverse (depth 3) | 30 | 80 | 150 |
| History: read last 50 | 10 | 20 | 40 |
| History: write entry | 10 | 20 | 40 |
| Feedback: write | 10 | 20 | 40 |
| Audit: write | 10 | 20 | 40 |
| Metrics: write | 5 | 10 | 20 |
| **KE API overhead (per call)** | **2** | **5** | **10** |

## 3. Schema Intelligence Latency

| Stage | Target | Max Acceptable |
|-------|--------|---------------|
| PostgreSQL connector full sync (200 tables) | < 10s | < 30s |
| LLM annotator (batch 50 columns) | < 30s | < 60s |
| Embedding generation (batch 100 items) | < 500ms | < 2s |
| Incremental sync (10 changed tables) | < 5s | < 15s |
| Relationship inference (200 tables) | < 5s | < 15s |

## 4. Learning Loop Latency

| Stage | Target | Notes |
|-------|--------|-------|
| Full batch cycle (1K feedback items) | < 30s | 5-minute cycle window |
| Feedback poll | < 100ms | Indexed query |
| Validation (1K items) | < 2s | SQL parsing using sqlglot |
| Q&A pair generation (top 100) | < 3s | LLM calls parallelized |
| Schema enrichment (top 20) | < 5s | One LLM call per column |
| Pattern mining (7-day window) | < 5s | Full scan of query_history |
| KE batch write | < 1s | Bulk insert |
| **Total batch cycle** | **< 16s** | **Well within 5-min window** |

## 5. Frontend Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Time to Interactive (TTI) | < 3.0s | Lighthouse |
| First Input Delay (FID) | < 100ms | Web Vitals |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Initial bundle size (JS) | < 200KB | Webpack analyze |
| API response to render | < 100ms | Browser DevTools |
| Offline fallback render | < 1s | Service worker |

## 6. Infrastructure Performance

| Component | Target | Measurement |
|-----------|--------|-------------|
| PostgreSQL query (simple, indexed) | < 5ms | pg_stat_statements |
| PostgreSQL query (complex, recursive CTE) | < 100ms | pg_stat_statements |
| Qdrant vector search (top 20, 100K points) | < 50ms | Qdrant metrics |
| Qdrant upsert (100 points) | < 100ms | Qdrant metrics |
| LLM inference (SQLCoder-7b, single) | < 500ms | vLLM metrics |
| LLM inference (Qwen2.5-72B, single) | < 2s | vLLM metrics |
| LLM inference (DeepSeek-V3, single) | < 4s | vLLM metrics |
| K8s pod startup time | < 5s | K8s events |
| Horizontal pod autoscaling reaction | < 30s | K8s HPA metrics |

## 7. Batch Operation Latency

| Operation | Target | Frequency |
|-----------|--------|-----------|
| Schema sync (full, 200 tables) | < 60s | On trigger |
| Schema sync (incremental, 10 tables) | < 15s | Every 24h |
| Learning loop batch cycle | < 30s | Every 5 min |
| Metrics rollup (hourly) | < 10s | Every hour |
| Metrics rollup (daily) | < 30s | Every day |
| Partition cleanup (drop old partitions) | < 5s | Daily |
| Backup (PG dump, 10GB database) | < 15min | Daily |

## 8. Budget Enforcement

Exceeded budgets trigger:

| Budget | Threshold | Action |
|--------|-----------|--------|
| Query total P95 > 10s | 3 consecutive measurements | Alert, investigate stage |
| Policy enforcement P95 > 500ms | Any measurement | Alert, optimize policy layers |
| KE API P95 > 50ms | 3 consecutive measurements | Alert, scale KE service |
| DB execution P95 > 5s | 5 consecutive measurements | Alert, analyze slow queries |
| Learning cycle > 60s | Any measurement | Alert, reduce batch size |
| Schema sync > 120s | Any measurement | Alert, optimize connector |
