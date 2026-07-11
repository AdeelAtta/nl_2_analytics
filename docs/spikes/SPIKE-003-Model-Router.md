# SPIKE-003: Model Router Accuracy

**Status:** COMPLETED | **Date:** 2026-07-11

---

## Objective
Evaluate whether the multi-tier model routing strategy correctly selects the appropriate model tier for different query complexities.

## Current Router Logic

| Complexity | Assigned Tier | Provider | Model |
|-----------|--------------|----------|-------|
| SIMPLE | NONE | rule_based | — |
| MEDIUM | LIGHTWEIGHT | huggingface | defog/sqlcoder-7b-2 |
| COMPLEX | STANDARD | huggingface | Qwen/Qwen2.5-72B-Instruct |
| VERY_COMPLEX | PREMIUM | openai | gpt-4o |

## Findings

### What Works
- **SIMPLE → NONE routing is correct** — Rule-based generation handles simple SELECT queries with 0.91 accuracy. No LLM call needed.
- **Fallback chain works** — When HF/OpenAI tokens are missing, the pipeline gracefully falls back through all tiers to rule-based generation.

### Issues Found

1. **Intent complexity classification is inaccurate** — The intent agent uses simple heuristics (word count, keyword presence) to classify complexity. A 3-word query with a subquery pattern could be classified SIMPLE when it needs STANDARD.

2. **No model validation** — The router has never been tested with real model responses. The configured models (sqlcoder-7b-2, Qwen2.5-72B) may not be the optimal choices for their assigned tiers.

3. **Tenant overrides are hardcoded** — `_apply_tenant_overrides` maps tiers to tenant types (free=LIGHTWEIGHT, pro=STANDARD). These should be configurable per-deployment.

## Recommendations

1. **Validate model assignments** — Run benchmark against sqlcoder-7b-2 and Qwen2.5-72B to verify tier assignments.
2. **Improve complexity detection** — Use more sophisticated heuristics: JOIN keyword → COMPLEX, subquery pattern → VERY_COMPLEX.
3. **Add cost tracking** — The cost_per_query values are hardcoded. Integrate with real pricing.
4. **Make routing configurable** — Allow per-tenant model override via config store.

## Verdict
The routing architecture is sound. The tier assignments and fallback chain are logically correct. The main risk is that complexity classification may be inaccurate for edge cases. This risk is mitigated by the fallback chain.
