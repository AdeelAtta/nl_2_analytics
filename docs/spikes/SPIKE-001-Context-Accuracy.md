# SPIKE-001: Context Layer Accuracy

**Status:** COMPLETED | **Date:** 2026-07-11

---

## Objective
Evaluate whether the current context retrieval (hybrid vector + keyword + DDL enrichment) provides accurate schema context for NL2SQL generation.

## Methodology

### Test Data
- 12 benchmark queries across 6 complexity levels (simple, aggregation, filter, join, sort, complex)
- 10 demo schema tables with 46 columns and 6 relationships
- Evaluated: table identification accuracy, filter extraction, join detection

### Context Retrieval Strategies

| Strategy | Implementation | Accuracy |
|----------|---------------|----------|
| **Keyword-only** | IntentAgent extracts table names from query text by matching schema names | 0.91 simple, 0.83 aggregation |
| **Keyword + schema** | Pipeline injects full demo schema context into merged_context | All tables available to planner |
| **Vector (mock)** | Not tested — BGE-M3 is mock only | N/A |

### Results

| Metric | Score | Assessment |
|--------|-------|-----------|
| Table identification | 0.92 | Strong — correctly identifies tables in 11/12 queries |
| Filter extraction | 0.75 | Good — status keywords and city extraction work. Date phrases partial. |
| Join detection | 0.43 | Weak — intent classifier rarely detects multi-table queries |
| Sort detection | 0.55 | Moderate — ORDER BY not consistently added |
| Overall benchmark | 0.787 | 91.7% pass rate at 0.5 threshold |

### Weaknesses Found

1. **Join detection is poor** — The intent classifier doesn't detect join patterns in natural language. "top 10 customers by order volume" doesn't trigger join intent because "customers" and "orders" as separate tables aren't detected as needing a join.
2. **ORDER BY missing** — Sort queries like "list employees by salary highest first" don't consistently produce ORDER BY clauses.
3. **Date phrases** — "last month", "this year" are extracted as filter values but not transformed into proper SQL date functions (e.g., `DATE_TRUNC('month', NOW())`).

### Recommendations

1. **Improve join detection** — Add join pattern recognition to IntentAgent (phrases like "by", "with", "and" between table names).
2. **Add ORDER BY support** — Enhance `_extract_sort` in the planner to detect sort intent and column references.
3. **Date normalization** — Add a date expression transformer that converts natural language dates to SQL date functions.
4. **Vector retrieval** — Replace mock BGE-M3 with real embeddings and validate that semantic retrieval improves context relevance.

## Verdict
The current context layer is adequate for simple to moderate complexity queries (91.7% pass rate). The primary gaps are join detection and sort handling. These are rule-based enhancements, not architectural changes.
