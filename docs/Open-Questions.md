# Open Questions

**Enterprise Data Intelligence Platform — Phase 0 Discovery**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 0.1 |
| **Cross-References** | [Technical-Landscape-Report.md](./Technical-Landscape-Report.md), [Research-Summary.md](./Research-Summary.md) |

---

## Purpose

This document captures all questions that could not be definitively answered during Phase 0 research. These represent:
- Assumptions that need validation
- Decisions that depend on further data
- External dependencies that require monitoring
- Trade-offs that need prototyping

Each question is categorized by type and prioritized by urgency.

---

## Question Categories

| Category | Meaning | Review Cadence |
|----------|---------|----------------|
| **TECH** | Technology decision requiring validation | Weekly during development |
| **PROD** | Product decision requiring customer input | Monthly during product validation |
| **BIZ** | Business decision requiring market data | Quarterly |
| **RSK** | Risk requiring monitoring | Ongoing |

---

## P0 — Must Answer Before MVP

| ID | Question | Category | Current Hypothesis | How to Answer | Owner |
|----|----------|----------|-------------------|---------------|-------|
| Q-001 | Can our autonomous schema discovery achieve >70% accuracy without any human input on enterprise schemas with poor naming conventions? | **TECH** | Yes, using LLM-based column description generation + query history mining + data profiling | Build a prototype schema scanner and evaluate on 5-10 real enterprise databases with varying schema quality | AI/ML Lead |
| Q-002 | What is the actual end-to-end latency of the LangGraph NL2SQL pipeline on a 2x MI300X setup? | **TECH** | <3s p95 for medium queries, <10s for complex | Run latency benchmark with full pipeline on target hardware | Infrastructure Lead |
| Q-003 | Does providing dialect documentation in the context improve accuracy enough to avoid SQL transpilation? | **TECH** | Yes, expecting 5-10% improvement vs no dialect context | A/B test with/without dialect docs on 500 queries per dialect | AI/ML Lead |
| Q-004 | What is the minimum number of Q&A pairs needed for the self-learning loop to reach 80% accuracy on a new schema? | **TECH** | ~100 for basic patterns, ~500 for comprehensive coverage | Simulate with public query log datasets, measure accuracy curve | AI/ML Lead |
| Q-005 | Can a 7B router model achieve >95% accuracy in classifying query complexity (simple/medium/complex)? | **TECH** | Yes, with 1000+ diverse training examples | Fine-tune Qwen2.5-7B on labeled query dataset, evaluate on held-out set | AI/ML Lead |

---

## P1 — Must Answer Before V1

| ID | Question | Category | Current Hypothesis | How to Answer | Owner |
|----|----------|----------|-------------------|---------------|-------|
| Q-006 | What is the actual TCO difference between AMD MI300X and NVIDIA H100 at 10K QPD for our specific workload? | **TECH** | AMD is 20-30% cheaper at equivalent throughput | Run identical benchmark on both platforms measuring throughput, latency, power, and cost/query | Infrastructure Lead |
| Q-007 | How should we handle schemas with 3000+ columns? Context compression vs progressive retrieval vs other? | **TECH** | Progressive retrieval — first filter by popularity/semantic match, then refine | Build benchmark with the Spider 2.0 dataset (largest schemas) | AI/ML Lead |
| Q-008 | What is the optimal strategy for handling ambiguous questions ("How did we do last month?")? | **PROD** | Intent disambiguation + user-specific defaults + clarification prompts | A/B test different disambiguation strategies with real users | Product Lead |
| Q-009 | How much manual context curation is acceptable in the "autonomous" product? (What is the minimum viable autonomy?) | **PROD** | MVP accepts 60-70% autonomy with "suggest edits" workflow | Customer interviews + prototype testing with target ICP | Product Lead |
| Q-010 | What pricing structure maximizes adoption for mid-market (50-500 employees)? | **BIZ** | $50/seat/month with 5-query/day free tier | A/B test pricing pages, competitor analysis, customer WTP surveys | CEO / Product |
| Q-011 | Which three databases should we support at MVP launch beyond PostgreSQL? | **PROD** | MySQL, Snowflake, BigQuery | Customer survey of target ICP | Product Lead |
| Q-012 | How do we handle real-time schema changes? Polling, CDC, event-driven? | **TECH** | Polling every 6 hours + manual refresh button | Evaluate CDC tools (Debezium, etc.) vs simple polling | Engineering Lead |
| Q-013 | What is the optimal chunking strategy for business documentation ingestion? | **TECH** | Semantic chunking with overlap, max 512 tokens per chunk | A/B test different chunking strategies on RAG accuracy | AI/ML Lead |

---

## P2 — Important But Not Blocking

| ID | Question | Category | Current Hypothesis | How to Answer | Owner |
|----|----------|----------|-------------------|---------------|-------|
| Q-014 | Should we build our own visualization component or integrate with existing BI tools (Metabase, Superset, etc.)? | **PROD** | Build lightweight inline visualization, integrate with BI tools via API | Customer interviews + technical evaluation | Product Lead |
| Q-015 | What is the right balance of AI-generated context vs human-curated context for the knowledge layer? | **PROD** | 80/20 AI/human split with human validation workflow | Usage analytics on context quality | Product Lead |
| Q-016 | Should we offer a semantic model API for BI tools (Cube-compatible) or focus on chat-first interface? | **PROD** | Chat-first MVP, semantic API in Phase 2 | Customer roadmap discussions | Product Lead |
| Q-017 | How should we handle queries that return sensitive/PII data? Masking? Filtering? Blocking? | **TECH** | Column-level RBAC + automatic PII detection + masking | Evaluate PII detection libraries (Presidio, etc.) + RBAC integration | Security Lead |
| Q-018 | Should we integrate with existing data catalogs (Alation, Collibra, DataHub) or replace them? | **PROD** | Integrate (read from) rather than replace | Customer discovery + technical evaluation | Product Lead |
| Q-019 | What is the optimal number of candidate SQL queries to generate per question? | **TECH** | 3 (temperature 0.3, 0.5, 0.7) | A/B test 1-5 candidates on accuracy vs latency | AI/ML Lead |
| Q-020 | How do we handle queries that require cross-database federation (e.g., Snowflake + Postgres join)? | **TECH** | Not supported in MVP; import/replicate for Phase 2 | Technical architecture design | Engineering Lead |
| Q-021 | What is the best approach for explaining why a query was rejected (by policy enforcement) to the user? | **PROD** | Layer-specific error messages + suggestion to rephrase | User testing | Product Lead |
| Q-022 | Should we offer a "confidence score" with each generated query? | **PROD** | Yes, model-level confidence + execution-level validation | User testing | Product Lead |

---

## P3 — Long-Term Research

| ID | Question | Category | Notes |
|----|----------|----------|-------|
| Q-023 | Can we build a fine-tuned model that matches GPT-4o on our specific NL2SQL workloads? | **TECH** | Requires accumulating 10K+ validated Q&A pairs |
| Q-024 | Should we use Knowledge Graphs (Neo4j) or can the vector store + relational DB handle Phase 2 requirements? | **TECH** | Depends on complexity of business relationship queries |
| Q-025 | What is the right approach for proactive insight generation (AI sending reports without being asked)? | **PROD** | Scheduled query patterns + anomaly detection |
| Q-026 | Should we build an agent for data quality monitoring (automated issue detection)? | **PROD** | Natural extension of schema intelligence |
| Q-027 | How do we handle real-time streaming data sources (Kafka, Kinesis) for near-real-time NL2SQL? | **TECH** | Materialized views + query-time freshness awareness |
| Q-028 | What is the right approach for multi-modal queries (text + charts + tables in one question)? | **TECH** | Emerging research area |
| Q-029 | Can we generate synthetic training data from schema descriptions to bootstrap the learning loop? | **TECH** | Related to Q-004 (cold start problem) |
| Q-030 | Should we build an agent marketplace (pre-built connectors, custom semantics) for enterprise customization? | **BIZ** | Platform play, Phase 3+ |

---

## External Dependencies to Monitor

| ID | Dependency | What We Need | Current Status | Monitoring |
|----|-----------|-------------|----------------|------------|
| D-001 | AMD ROCm investment | Continued investment and compatibility improvements | Strong (ROCm 6.3+, major model support) | Track ROCm releases, developer sentiment |
| D-002 | vLLM ROCm support | Ongoing compatibility with latest models | Production-grade | Track vLLM ROCm changelog, benchmarks |
| D-003 | OpenAI API pricing | No dramatic price increases | Stable | Monitor pricing page, quarterly review |
| D-004 | LangGraph maturity | Stable API, production reliability | Growing fast (weekly releases) | Track changelog, bug reports |
| D-005 | Qwen model availability | Continued updates and community support | Strong (Alibaba-backed) | Monitor releases, community activity |
| D-006 | Snowflake/Databricks cross-database features | If they add multi-DB support, our moat narrows | Not on roadmap (per public docs) | Quarterly competitive review |
| D-007 | MCP protocol adoption | If MCP becomes universal, we need compatibility | Growing (Anthropic + community) | Track MCP adoption, spec changes |

---

## Decisions Deferred

| Decision | Why Deferred | Trigger for Decision |
|----------|-------------|---------------------|
| Monorepo vs polyrepo | Need to understand team size and domain boundaries | After Phase 1 (team structure defined) |
| AWS vs Azure vs GCP | Need customer geography data | After customer validation |
| Go for performance-critical path | Python may be sufficient for MVP | When Python performance becomes bottleneck |
| Build MCP server | Depends on MCP adoption pace | When >20% of enterprise AI tools adopt MCP |
| On-prem deployment (SaaS vs self-hosted) | Need customer demand | When >3 enterprise customers request on-prem |
| White-label/embedded product | Need partner interest | When data platform companies express interest |

---

## Next Steps for Open Questions

1. **Q-001 through Q-005** → Must be answered during Phase 1 (Engineering Planning) through targeted prototypes and benchmarks
2. **Q-006 through Q-013** → Must be answered before V1 architecture is frozen
3. **Q-014 through Q-022** → Tracked for Phase 2 planning
4. **Q-023 through Q-030** → Long-term research, revisit quarterly
5. **External dependencies** → Monitor monthly, escalate if risk level changes
6. **Deferred decisions** → Revisit when trigger conditions are met
