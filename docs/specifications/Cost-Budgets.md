# Cost Budgets

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

---

## 1. Per-Query Cost Model

This is the single most important financial metric. Every query generates inference cost. We must keep the weighted average below $0.006/query to maintain margin targets.

| Model Tier | Cost per Query | % of Queries | Weighted Cost |
|------------|---------------|-------------|---------------|
| SQLCoder-7b-2 (simple) | $0.0003 | 50% | $0.00015 |
| Qwen2.5-72B (medium) | $0.002 | 35% | $0.00070 |
| DeepSeek-V3 (complex) | $0.01 | 10% | $0.00100 |
| GPT-4o (fallback) | $0.02 | 5% | $0.00100 |
| **Weighted average** | — | 100% | **$0.00285** |

**Safety buffer**: 2x multiplier for retries, repairs, reflection cycles = **~$0.0057/query**

### Cost Breakdown by Pipeline Stage

| Stage | Cost per Query | Includes |
|-------|---------------|----------|
| Intent classification | $0.0001 | Small model or rule-based |
| Query embedding | $0.00001 | BGE-M3 (negligible) |
| Context retrieval | $0.0001 | Qdrant read + DB reads |
| SQL generation (primary) | $0.00285 | Weighted avg across tiers |
| Validation | $0.00005 | sqlglot parse (no LLM) |
| Repair (avg 0.3x queries) | $0.0003 | 30% of queries need repair |
| Reflection | $0.0001 | LLM-based critique |
| Policy Enforcement (L2-L10 deterministic) | $0.00001 | Rule-based (no LLM) |
| **Total per query** | **~$0.0034** | — |

### Revenue per Query by Tier

| Plan | Monthly Seat | Est. Queries/Seat | Revenue/Query | Cost/Query | Gross Margin |
|------|-------------|-------------------|---------------|------------|-------------|
| Free | $0 | 50 | $0.00 | $0.0034 | -∞ (loss leader) |
| Starter | $50 | 200 | $0.25 | $0.0034 | 98.6% |
| Pro | $150 | 1,000 | $0.15 | $0.0034 | 97.7% |
| Enterprise | Custom | Custom | ~$0.10 | $0.0034 | ~96.6% |

## 2. Infrastructure Cost per Tenant

### SaaS (Shared) — $206/tenant/month → $47/tenant/month at scale

| Component | Unit | Unit Cost | Per Tenant/Month |
|-----------|------|-----------|-----------------|
| PostgreSQL (shared, 10 tenants/instance) | db.r6g.large | $200/mo | $20 |
| Qdrant (shared, 10 tenants/instance) | m6i.xlarge | $250/mo | $25 |
| GPU inference (shared, 50 tenants/node) | mi300x.4xlarge | $5,000/mo | $100 |
| CPU nodes (shared, 50 tenants/node) | m6i.large | $2,500/mo | $50 |
| Storage (S3, backup, logs) | 50GB/tenant | $0.023/GB | $1.15 |
| Data transfer | 10GB/tenant | $0.09/GB | $0.90 |
| Monitoring & ops | per-tenant allocation | — | $5 |
| **Per-tenant cost (startup)** | — | — | **~$202** |
| **Per-tenant cost (at scale, 1K tenants)** | — | bulk discount | **~$47** |

### Target Gross Margin by Scale

| Scale | Tenants | Revenue/tenant/mo | Cost/tenant/mo | Gross Margin |
|-------|---------|-------------------|---------------|--------------|
| Early | 10 | $75 (mix) | $202 | -169% (R&D investment) |
| Growth | 100 | $125 (mix) | $95 | 24% |
| Scale | 1,000 | $145 (mix) | $47 | 67% |
| Target | 10,000 | $150 (mix) | $35 | 77% |

## 3. Embedding Cost

| Operation | Model | Cost per 1K items | Batching |
|-----------|-------|-------------------|----------|
| Initial schema sync (200 tables) | BGE-M3 | ~$0.02 | Embed 100 at a time |
| Incremental sync (10 changed tables) | BGE-M3 | ~$0.001 | Single batch |
| Query embedding | BGE-M3 | ~$0.00001 | Single item |
| Learning loop re-embedding | BGE-M3 | ~$0.01/batch | Batch of 50 |

BGE-M3 is self-hosted (no API cost). Costs are compute-only (GPU electricity).

## 4. Storage Cost

| Data | Volume/Tenant/Month | Cost/Tenant/Month |
|------|--------------------|-------------------|
| PostgreSQL data | 500MB | ~$2.00 |
| PostgreSQL backup | 1GB (daily, 30-day retention) | ~$0.69 |
| Qdrant vectors | 200MB (20K vectors * 1024d * 4 bytes) | ~$0.80 |
| Qdrant snapshots | 400MB (daily, 7-day retention) | ~$0.28 |
| Logs (Loki) | 100MB | ~$0.05 |
| Traces (Tempo) | 50MB | ~$0.03 |
| **Total storage** | **~2.25GB** | **~$3.85** |

## 5. GPU Cost

### Self-Hosted vs Cloud Inference

| Scenario | Cost/1M tokens | Monthly for 100K queries | Annual |
|----------|---------------|-------------------------|--------|
| SQLCoder-7b-2 (self-hosted, AMD MI300X) | $0.15 | $15 | $180 |
| Qwen2.5-72B (self-hosted, AMD MI300X) | $0.50 | $175 | $2,100 |
| DeepSeek-V3 (self-hosted, 2x MI300X) | $1.50 | $150 | $1,800 |
| GPT-4o (API, fallback only) | $10.00 | $50 | $600 |
| **Total self-hosted primary** | — | **$390** | **$4,680** |
| **Total if all queries via GPT-4o** | — | **$20,000** | **$240,000** |
| **Savings with self-hosted + routing** | — | **$19,610/mo** | **$235,320/yr** |

## 6. Cost Optimization Levers

| Lever | Impact | Complexity | Timeline |
|-------|--------|-----------|----------|
| Increase self-hosted routing % (target > 95%) | $5K/mo saved per % moved from GPT-4o | Medium | Ongoing |
| Batch LLM inference for learning loop | Reduce learning GPU cost by 40% | Low | Week 1 |
| SQLCoder-7b-2 optimizations (quantization, KV cache) | 2x throughput on same GPU | Medium | Month 2 |
| Qdrant on_disk_payload for less RAM | Reduce node size by 30% | Low | Month 1 |
| Reduce GPT-4o fallback from 5% to 2% | $300/mo saved at 100K queries | Medium | Month 3 |
| Cache common schema queries | Reduce Qdrant reads by 40% | Low | Week 2 |

## 7. Cost Tracking

Every query response includes cost breakdown:

```json
{
  "cost": {
    "total": 0.0034,
    "breakdown": {
      "intent": 0.0001,
      "embedding": 0.00001,
      "retrieval": 0.0001,
      "generation": 0.00285,
      "validation": 0.00005,
      "repair": 0.0003,
      "reflection": 0.0001,
      "policy_enforcement": 0.00001
    },
    "model_used": "qwen2.5-72b",
    "tokens_in": 2840,
    "tokens_out": 312,
    "cache_hit": false
  }
}
```

## 8. Cost Alert Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| Daily query cost per tenant | > $0.50 | Investigate usage pattern |
| Monthly GPU utilization | < 60% | Consolidate or downsize |
| GPT-4o fallback rate | > 10% of queries | Tune model router |
| Per-query cost (weighted avg) | > $0.006 | Review routing decisions |
| Inference tokens per query | > 8K avg | Optimize prompt templates |
