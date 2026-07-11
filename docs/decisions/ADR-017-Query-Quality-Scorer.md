# ADR-017: Query Quality Scorer

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-017 |
| **Date** | 2026-07-11 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Generated SQL queries vary widely in quality depending on the model, prompt, and schema context. The platform needs a mechanism to evaluate query quality along multiple dimensions — correctness, efficiency, safety, readability, and schema alignment — to surface poor results, enable monitoring, and provide feedback for model improvement. The scorer must be non-blocking (quality must not gate query execution) and support both rule-based heuristic scoring for speed and optional LLM-based judging for deeper analysis.

## Decision

Implement a hybrid `QueryQualityScorer` that evaluates SQL queries on five weighted dimensions:

| Dimension | Weight | Evaluation |
|-----------|--------|------------|
| Correctness | 30% | Rule-based — checks for syntax validity via sqlglot parse |
| Efficiency | 25% | Rule-based — detects full table scans, missing LIMIT, N+1 patterns |
| Safety | 20% | Rule-based — detects DML, DDL, destructive operations |
| Readability | 10% | Heuristic — scores based on formatting, formatting consistency |
| Schema Alignment | 15% | Rule-based — validates column/table references against known schema |

The overall score is `SUM(dimension.score * dimension.weight)` on a 0.0–1.0 scale. An optional LLM judge can override or augment individual dimension scores.

Key design decisions:

- **Non-blocking**: Quality scoring runs after SQL generation and does not block execution. The score is recorded in `PipelineResult.quality_score` for observability.
- **Pipeline integration**: The `PipelineOrchestrator` accepts an optional `QueryQualityScorer`. When `enable_quality=True` and a scorer is provided, it runs after the `generate` stage.
- **Weighted composite**: The composite score gives a single-number summary while dimension scores allow targeted analysis.
- **Lazy LLM import**: The optional LLM judge is lazy-imported from `InferenceFactory` to avoid hard dependencies.

## Rationale

- **Rule-based first**: Fast (< 5ms per query), deterministic, and works offline. Covers the majority of quality issues (invalid syntax, missing LIMIT, dangerous DML).
- **Optional LLM judge**: Adds depth at the cost of latency and cost. Useful for training data curation and detailed feedback loops.
- **Weighted composite**: Aligns with standard evaluation frameworks (e.g., BLEU, ROUGE) while being domain-specific to SQL.
- **Non-blocking**: Query execution is the primary path; quality is a monitoring concern, not a gate.
- **Five dimensions**: Cover the full surface of query quality — correctness, performance, security, maintainability, and semantic accuracy.

## Consequences

### Positive
- Provides actionable quality signals for monitoring, alerting, and model improvement
- Hybrid architecture scales from lightweight rule checks to deep LLM analysis
- Non-blocking design avoids introducing failure points in the critical query path

### Negative
- LLM-based judging adds latency and API cost when enabled
- Rule-based heuristics may produce false negatives for subtle semantic issues
- Dimension weights are manually tuned and may need adjustment per deployment

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Pure LLM judging | Too slow and expensive for production use; introduces external dependency on every generation |
| Single composite score without dimensions | Lacks actionable granularity — teams can't tell if a low score is due to safety vs efficiency |
| Blocking scorer (gate execution on quality) | Increases latency and risk; a false-negative quality score would deny valid queries |

## References

- `ke/services/quality_scorer.py` — `QueryQualityScorer` implementation
- `ke/models/quality.py` — `QualityDimension`, `QualityDimensionScore`, `QualityScore` models
- `ke/services/pipeline.py` — Integration in `PipelineOrchestrator`
