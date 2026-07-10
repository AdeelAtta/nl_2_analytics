# Research Summary

**Enterprise Data Intelligence Platform — Phase 0 Discovery**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 0.1 |
| **Cross-References** | [Technical-Landscape-Report.md](./Technical-Landscape-Report.md), [Technology-Recommendations.md](./Technology-Recommendations.md) |

---

## 1. Consolidated Findings

### 1.1 The Core Problem

| Finding | Evidence | Source |
|---------|----------|--------|
| Enterprise NL2SQL accuracy drops from 85% (benchmark) to 10-21% (production) | Spider 2.0: GPT-4o achieves 10.1%, o1-preview achieves 17.1% | Spider 2.0 paper (ICLR 2025), arXiv:2411.07763 |
| Four recurring failure modes: ambiguous intent, missing business knowledge, physical schema complexity, context sensitivity | Oracle OCI NL2SQL team | Oracle Cloud blog (Sujeeth Bharadwaj et al.) |
| 68% of enterprise data goes unanalyzed due to silos | IBM | Industry research |
| 40-60% of analyst time is spent writing routine SQL queries | Multiple surveys | Consensus finding |

### 1.2 Technology Consensus

| Finding | Evidence | Source |
|---------|----------|--------|
| Multi-agent pipelines outperform single-shot prompting by 15-30% | Benchmark of Vanna (40%) vs WrenAI (22%) vs DB-GPT (20%) | Sudipta Pathak benchmark (Feb 2026) |
| Pre-computed schema embeddings outperform per-request embeddings | LitE-SQL: 88.45% on Spider, 2-30x fewer parameters | LitE-SQL paper (EACL 2026) |
| Semantic Layer approaches 100% accuracy for modeled queries | dbt Labs 2026 benchmark | dbt Developer Blog (Apr 2026) |
| RAG with examples is the best single approach for NL2SQL | Vanna's RAG-first approach benchmarked highest | Sudipta Pathak (Feb 2026) |
| GraphRAG reduces hallucinations by 60% on complex queries | Zylos AI / Datalinkk | Enterprise research (Feb 2026) |
| 7-layer guardrail stack is production standard | ASK-TARA: 90K queries, zero security incidents | N1N / Dev.to (May 2026) |

### 1.3 Market Findings

| Finding | Evidence | Source |
|---------|----------|--------|
| Agentic AI market projected from $7.55B (2025) to $199B (2034) | 43.84% CAGR | Gartner / Multi-Agent Systems whitepaper |
| 40% of enterprise software will integrate AI agents by end of 2026 | Up from <5% in 2025 | Gartner |
| Only 2% of enterprises have deployed agentic AI at full production scale | Pilot-to-production gap | Ampcome / Gartner 2026 |
| All three major warehouse vendors have native AI, all are single-platform | Snowflake, Databricks, Google | Product documentation |

### 1.4 Inference Findings

| Finding | Evidence | Source |
|---------|----------|--------|
| vLLM, SGLang, llama.cpp all have production-grade ROCm support | AMD official documentation | ROCm docs / AMD blogs |
| HuggingFace TGI moved to maintenance mode (March 2026) | Official announcement | HuggingFace |
| SGLang recommended for agent/structured output workloads | Performance benchmarks | vLLM vs SGLang comparison (Mar 2026) |
| AMD MI300X (192GB) capable of running DeepSeek-V3 class models | AMD/SGLang integration | AMD Developer Cloud docs |

---

## 2. Key Assumptions

These are assumptions that require validation during development:

| # | Assumption | Risk Level | Validation Method |
|---|-----------|------------|-------------------|
| A-1 | Autonomous schema discovery can achieve >70% accuracy without human input | Medium | Prototype with 10 enterprise schemas |
| A-2 | Tiered model routing will reduce inference costs by 50-70% | Low | Production cost tracking |
| A-3 | Self-learning loop converges within 500 queries per domain | Medium | Simulation with public query logs |
| A-4 | AMD ROCm provides 20-30% TCO advantage over NVIDIA for our workload | Medium | Standardized benchmark |
| A-5 | Cross-database NL2SQL accuracy is within 5% of single-database accuracy | High | Multi-DB evaluation |
| A-6 | Mid-market enterprises (50-500 employees) will pay $50/seat/month | Medium | Customer interviews |
| A-7 | LangGraph can achieve <2s p95 latency for the full NL2SQL pipeline | Medium | Latency benchmark |
| A-8 | SQL dialect differences can be handled by context alone (no transpilation) | Medium | Dialect accuracy comparison |

---

## 3. Hypotheses Being Validated

| # | Hypothesis | Expected Outcome | Test |
|---|-----------|------------------|------|
| H-1 | "Autonomous context layer is the key differentiator" | Customers choose us over Cortex Analyst/Genie because no YAML setup needed | Competitive demo comparison |
| H-2 | "Cross-database support is a primary purchase criterion" | 60%+ of customers cite multi-DB as top-3 requirement | Customer survey |
| H-3 | "Self-improving accuracy creates switching costs" | Accuracy improves 10%+ per quarter with active use | Longitudinal accuracy tracking |
| H-4 | "AMD-first inference enables 30%+ better margins" | Inference cost < $0.005/query average | Cost accounting per query |
| H-5 | "2s response time is acceptable for complex analytical queries" | <5% abandonment rate at 3s | User behavior analytics |

---

## 4. Confirmed Facts

| # | Fact | Evidence |
|---|------|----------|
| F-1 | Multi-agent architectures are the dominant production paradigm | All major production systems use 3-7 specialized agents |
| F-2 | Deterministic guardrails are essential for production safety | ASK-TARA (90K queries, zero incidents) |
| F-3 | Schema size correlates inversely with NL2SQL accuracy | Spider 1.0 (10 tables) → 85% vs Spider 2.0 (1000+ cols) → 17% |
| F-4 | Business knowledge must be explicitly modeled | All successful production deployments have a semantic/knowledge layer |
| F-5 | Query history is the single best source of schema relationship data | Vanna, LinkedIn SQL Bot, and others use this as primary signal |
| F-6 | Open-source LLMs have reached parity with commercial for SQL generation | SQLCoder-7b-2 outperforms GPT-4 on complex ratio queries |
| F-7 | AMD ROCm is production-viable for LLM inference | vLLM, SGLang, llama.cpp all have production-grade ROCm support |
| F-8 | No product currently offers autonomous semantic discovery | Confirmed by competitive analysis of 15+ products |

---

## 5. Likely Trends (2026-2028)

| Trend | Confidence | Impact |
|-------|-----------|--------|
| Multi-agent architectures become the default for all enterprise AI interactions | High | Our architecture choice is validated |
| Open-source LLMs surpass commercial for domain-specific NL2SQL | High | Fine-tuned SQL models will become critical infrastructure |
| GraphRAG replaces pure vector RAG for enterprise knowledge retrieval | Medium-High | Knowledge graph should be in plan for Phase 2 |
| MCP (Model Context Protocol) becomes universal standard | Medium | Build MCP-compatible API |
| AMD captures 15-20% of AI inference market | Medium | AMD-first strategy de-risked |
| Warehouse-native AI products add cross-database support | Low (2-3 year timeline) | Current competitive moat is temporary |
| Fine-tuned 7B models match prompted 70B models for specific tasks | High | SQLCoder trend validates this |
| Cost-per-token drops 50%+ annually | Very High | Inference abstraction becomes more important |

---

## 6. Divergent Expert Opinions

| Topic | Consensus | Dissenting View | Our Position |
|-------|-----------|-----------------|--------------|
| Semantic Layer vs RAG for NL2SQL | Semantic Layer is more accurate; RAG is more flexible | "RAG with examples alone can match SL accuracy" (Vanna) | Hybrid: autonomous SL + RAG augmentation |
| Multi-agent vs monolithic pipeline | Multi-agent is better for complex queries | "Adds latency without proportional accuracy gain" (some production teams) | Multi-agent with fast-path for simple queries |
| AMD vs NVIDIA for inference | NVIDIA is still the standard | "AMD TCO advantage is 20-30% for inference" | AMD-first with NVIDIA fallback via abstraction |
| Self-hosted vs cloud API models | Cloud APIs are simpler for startups | "Self-hosted is cheaper at scale and provides data privacy" | Hybrid: self-hosted primary, cloud fallback |
| Fine-tuning vs prompting | Prompting is sufficient for most cases | "Fine-tuned domain models beat prompted general models" | Prompting for MVP, fine-tuning for V1+ |

---

## 7. Sources by Category

### 7.1 Academic Papers
- Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows (ICLR 2025)
- LitE-SQL: Schema Embeddings with Contrastive Learning (EACL 2026)
- BIRD: Big Bench for Large-scale Database Grounded Text-to-SQL (NeurIPS 2023)
- A Survey of Text-to-SQL in the Era of LLMs (IEEE TKDE 2025)
- Natural Language to SQL: State of the Art and Open Problems (VLDB 2025)
- The Dawn of Natural Language to SQL: Are We Fully Ready? (VLDB 2024)

### 7.2 Enterprise Products
- Snowflake Cortex Analyst: Product documentation (2025-2026)
- Databricks AI/BI Genie: Product documentation (2025-2026)
- Oracle OCI NL2SQL (SQL Search): Product documentation (2026)
- Google BigQuery Gemini: Product documentation (2025-2026)
- Microsoft Copilot for Fabric: Product documentation (2025-2026)
- ThoughtSpot Spotter: Product documentation (2025-2026)

### 7.3 Open-Source Projects
- Vanna AI (GitHub ~22K stars): Codebase analysis
- WrenAI (GitHub ~14K stars): Codebase analysis
- DB-GPT (GitHub ~17K stars): Codebase analysis
- SQLCoder (GitHub ~4K stars): Model documentation
- LangGraph (GitHub ~10K stars): Framework documentation
- LLama.cpp, vLLM, SGLang: Documentation and benchmarks

### 7.4 Engineering Blogs & Analysis
- AWS/Cisco: Enterprise-grade NL2SQL (Apr 2025)
- Oracle OCI: Enterprise NL2SQL with Semantic Enrichments (2026)
- dbt Labs: Semantic Layer vs Text-to-SQL Benchmark (Apr 2026)
- InfiniSynapse: Best NL2SQL Tools 2026 (May 2026)
- N1N: 7-Layer NL2SQL Guardrail Stack (May 2026)
- Sudipta Pathak: NL2SQL Benchmark Vanna vs WrenAI vs DB-GPT (Feb 2026)
- InfiniSynapse: NL2SQL Benchmark Spider BIRD (Jun 2026)
- VRLA Tech: LLM Inference Engine Comparison 2026 (Jun 2026)
- N1N: LLM Inference Engine Comparison (Mar 2026)

### 7.5 Market Research
- Gartner: Multiagent Systems in Enterprise AI (2026)
- Gartner: 40% of enterprise software to integrate AI agents by 2026
- Gartner: $12.9M average annual loss from poor data quality
- Accenture: Intelligent Digital Brain architecture (2026)
- Dataiku/Harris Poll: 74% of CIOs regret AI vendor selection (2026)
- Cloudera: State of Enterprise AI (2025)

### 7.6 Infrastructure & Hardware
- AMD ROCm 6.3 Documentation
- AMD: vLLM on ROCm Benchmark Docker
- AMD: SGLang on ROCm Benchmark Docker
- AMD: llama.cpp on ROCm Documentation
- Lushbinary: Vector Database Comparison (May 2026)
- Inductivee: Vector Database Benchmarks (Apr 2026)
- Internative: Best Vector Databases 2026 (Jun 2026)
