# AI System Assessment

**Score: 68/100 — PARTIALLY VERIFIED**

---

## 1. Architecture Classification

**Verdict:** The architecture is **beyond standard RAG** but falls short of genuine autonomous schema understanding. It combines:
- Standard RAG (vector + keyword retrieval)
- Rule-based intent classification
- Multi-tier model routing with reflection
- 10-layer deterministic guardrail stack
- Learning loop for continuous improvement

This is a **hybrid architecture** — more sophisticated than naive RAG but not fully autonomous.

## 2. Component Analysis

| Component | Status | Evidence |
|-----------|--------|----------|
| Schema Discovery | ✅ Implemented | 5 DB connectors (PG, MySQL, Snowflake, BigQuery, DuckDB) with full schema extraction |
| Schema Adaptation | ⚠️ Partial | Rule-based + optional LLM annotator. No real-time schema change detection. |
| Context Layer | ✅ Implemented | Hybrid search (dense + sparse), DDL enrichment, relationship context |
| Ontology | ✅ Implemented | Graph store with recursive CTE traversal, node types, edge types, import/export |
| Semantic Retrieval | ⚠️ Partial | Vector search implemented. Embeddings are mock/deterministic — never tested with real BGE-M3. |
| Hybrid Retrieval | ⚠️ Implemented | Dense prefetch + sparse rerank with `dense_weight` config. Never benchmarked. |
| Planner | ✅ Implemented | QueryIntent → QueryPlan with validation, feasibility checks |
| SQL Generation | ✅ Implemented | Rule-based (for simple) + model-based (for complex) with multi-candidate generation |
| Reflection | ✅ Implemented | Self-critique loop using MockClient (reflection template evaluates generated SQL) |
| Validator | ✅ Implemented | 10-layer guardrail stack — all deterministic except L1 (intent classification) |
| Execution | ✅ Implemented | SQL execution with timeout, pagination, dry-run, error classification |
| Learning Engine | ✅ Implemented | Feedback collection → validation → QA pair building → schema enrichment → pattern mining |
| Prompt Management | ✅ Implemented | Template-based system with 3 templates (standard, simple, reflection) |

## 3. Critical Findings

### 3.1 HIGH: Never Validated Against Real Models
The entire pipeline has never been tested with real LLM inference. The `InferenceFactory` returns `MockClient` for all providers when API keys are missing. The reflection agent uses `MockClient`. The quality scorer's LLM judge has never judged a real query.

**Evidence:** `ke/services/inference.py:154-163` — `create()` returns MockClient when HF token or OpenAI key is missing. `ke/services/generator.py:213` — `MockClient("reflection")` used for SQL reflection.

**Impact:** SQL generation accuracy, reflection quality, and overall pipeline accuracy are completely unknown. The system may work well or may fail catastrophically with real models.

### 3.2 HIGH: Cold-Start Strategy Not Researched
SPIKE-002 (Cold-Start Strategy) is one of three unstarted research spikes. The system has no strategy for handling empty/unknown schemas. Currently, when no schema context is available, the pipeline falls back to extracting words from the user query, which produces plausible-looking but semantically meaningless SQL.

**Evidence:** `docs/epics/EP-017-Research-Spikes.md` — SPIKE-002 status: "not started". `ke/services/generator.py:229-237` — fallback `_rule_based_generate` extracts words from query when no tables detected.

### 3.3 MEDIUM: Model Router Accuracy Unknown
SPIKE-003 (Model Router Accuracy) is not started. The router uses a hardcoded complexity-to-tier mapping (`SIMPLE → NONE, MEDIUM → LIGHTWEIGHT, COMPLEX → STANDARD, VERY_COMPLEX → PREMIUM`). This mapping has never been validated against real query distributions.

**Evidence:** `ke/services/router.py:38-43` — hardcoded `ROUTE_RULES` mapping. No accuracy benchmarks exist.

## 4. Is This State-of-the-Art?

**No.** The architecture is well-designed and incorporates many best practices (guardrails, reflection, hybrid retrieval, learning loop), but it lacks the key differentiators that define state-of-the-art Text-to-SQL systems:

| Capability | Status | SOTA Comparison |
|-----------|--------|-----------------|
| Self-adaptive schema understanding | ❌ Not implemented | DAIL-SQL, MAC-SQL adapt to schema dynamically |
| Multi-turn conversation state | ✅ Implemented | Session support with history injection |
| User feedback integration | ✅ Implemented | Learning loop with QA pairs |
| Cost-aware model routing | ✅ Implemented | Tiered routing with cost tracking |
| Cross-database generalization | ⚠️ Partial | Research needed (SPIKE-001/003) |
| Automatic error correction | ✅ Implemented | Reflection agent + repair |
| Execution-guided generation | ⚠️ Partial | Dry-run validates SQL but doesn't feed back into generation |
| Few-shot example selection | ❌ Not implemented | No dynamic example selection based on query similarity |

**AI System Verdict: 68/100 — Well-designed architecture that cannot be validated without real model integration. Research spikes must be completed before GA.**
