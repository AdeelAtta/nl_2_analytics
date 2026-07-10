# Research Bibliography

**Enterprise Data Intelligence Platform — Phase 0 Discovery**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 0.1 |
| **Cross-Reference** | [Technical-Landscape-Report.md](./Technical-Landscape-Report.md) |

---

## 1. Academic Papers

| # | Citation | Key Finding |
|---|----------|-------------|
| 1 | Lei, F. et al. "Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows." ICLR 2025 (Oral). arXiv:2411.07763. | Enterprise NL2SQL is fundamentally unsolved: o1-preview solves only 17.1% of tasks. GPT-4o: 10.1%. |
| 2 | Li, G. et al. "Natural Language to SQL: State of the Art and Open Problems." VLDB 2025. | Comprehensive survey of NL2SQL approaches and open challenges. |
| 3 | Liu, X. et al. "A Survey of Text-to-SQL in the Era of LLMs: Where are we, and where are we going?" IEEE TKDE 2025. | Multi-agent architectures and RAG are the dominant trends in 2025-2026. |
| 4 | Li, J. et al. "The Dawn of Natural Language to SQL: Are We Fully Ready?" VLDB 2024. | Identified key gaps between academic benchmarks and production requirements. |
| 5 | Qi, J. et al. "LitE-SQL: Schema Embeddings with Contrastive Learning." EACL 2026. | Pre-computed schema embeddings with contrastive learning achieve 88.45% on Spider with 2-30x fewer parameters. |
| 6 | Li, J. et al. "BIRD: Big Bench for Large-scale Database Grounded Text-to-SQL." NeurIPS 2023. | Introduced the BIRD benchmark with 12,751 Q&A pairs across 95 databases. |
| 7 | Hu, E. J. et al. "LoRA: Low-Rank Adaptation of Large Language Models." ICLR 2022. | Foundation for efficient fine-tuning of SQL-specific models. |
| 8 | Lewis, P. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. | Foundation for RAG architecture used in modern NL2SQL. |

---

## 2. Enterprise Product Documentation

| # | Product | Source | Key Insight |
|---|---------|--------|-------------|
| 9 | Snowflake Cortex Analyst | docs.snowflake.com (2025-2026) | Requires YAML semantic model; Snowflake-only. Semantic views added Nov 2025. |
| 10 | Databricks AI/BI Genie | docs.databricks.com (2025-2026) | Requires Unity Catalog curation + trusted assets. Genie Spaces model. |
| 11 | Oracle OCI NL2SQL (SQL Search) | docs.oracle.com (2026) | Semantic enrichment as a shared layer; two-connection pattern (enrichment + query). |
| 12 | Google BigQuery Gemini | cloud.google.com/bigquery (2025-2026) | Multi-step pipeline: intent → schema selection → SQL generation → validation. Uses Dataform. |
| 13 | Microsoft Copilot for Fabric | learn.microsoft.com/fabric (2025-2026) | Routes through Power BI semantic model (measures, relationships, hierarchies). |

---

## 3. Engineering Blogs & Technical Analysis

| # | Article | Source | Key Insight |
|---|---------|--------|-------------|
| 14 | "Building a 7-Layer NL2SQL Guardrail Stack for Enterprise Grade AI" | N1N / Dev.to (May 2026) | ASK-TARA: 90K queries, zero incidents. Fail-closed architecture. |
| 15 | "Best practices to improve NL2SQL accuracy with Oracle Select AI" | Oracle Blogs (Jun 2026) | AI profile is the control plane; metadata enrichment is critical. |
| 16 | "Enterprise-grade NL2SQL using LLMs" | AWS Machine Learning Blog (Apr 2025) | Joint AWS/Cisco pattern: complex schemas, simpler models, cost-effective. |
| 17 | "NL2SQL in 2026: How Multi-Agent Pipelines Convert NL to Safe SQL" | Dev.to (Apr 2026) | DDL vector stores replacing per-request embeddings. Multi-agent validation pattern. |
| 18 | "NL2SQL in 2026: Bridging Benchmarks and Production" | Medium / Fred Zhang (2026) | Multi-agent architectures + domain knowledge + governance = production success. |
| 19 | "Semantic Layer vs. Text-to-SQL: 2026 Benchmark Update" | dbt Developer Blog (Apr 2026) | Semantic layer approaches 100% accuracy. Text-to-SQL better for ad hoc. Hybrid is ideal. |
| 20 | "What is NL2SQL? A 2026 Practical Guide" | InfiniSynapse (May 2026) | Four layers: schema linking → generation → validation → execution. |
| 21 | "Dissecting Open-Source NL2SQL: Vanna vs WrenAI vs DB-GPT" | Sudipta Pathak (Feb 2026) | Three architectural paradigms: RAG-first, semantic-first, multi-agent-first. |
| 22 | "NL2SQL Benchmark: Vanna AI vs WrenAI vs DB-GPT" | Sudipta Pathak (Feb 2026) | Vanna 40% > WrenAI 22% > DB-GPT 20% on 50-query benchmark with same LLM. |
| 23 | "Building an Enterprise NL2SQL AI Assistant: Lessons Learned" | Medium / Cisco (Feb 2025) | Data architecture is key. Schema info alone is insufficient. Supervisor agent architecture. |
| 24 | "Why NL2SQL Fails in Enterprise Deployments" | Medium / Arisyn (Jun 2026) | Semantic mapping + query validation are the two keys to success. |
| 25 | "Enterprise NL2SQL: The Real Bottleneck Isn't the AI — It's Your Metadata" | Medium / Annmol Hattikudur (Mar 2026) | Three tiers of enterprise adoption. Metadata management defines success. |
| 26 | "The Future of AI/BI: Snowflake Cortex Analyst vs Databricks Genie" | ColRows (Jun 2026) | Both warehouse-native. Key difference: Cortex Analyst is API-first, Genie is chat-first. |
| 27 | "Snowflake vs Databricks: Why You Need an Autonomous Semantic Layer" | ColRows (Jun 2026) | Warehouse-native AI is single-platform. Autonomous semantic layer is the solution. |
| 28 | "Cortex Analyst vs Genie vs BigQuery Gemini" | Agami AI (Jun 2026) | All three share the same blind spot: locked into their cloud. |
| 29 | "Enterprise Agentic AI Platform Architecture: 2026 Complete Guide" | Ampcome (May 2026) | <2% of enterprises at full production scale. The gap is architectural, not technological. |
| 30 | "Building a Dynamic Multi-Agent Enterprise Platform" | Oracle AI & Data Science Blog (Apr 2026) | Agent-to-Agent (A2A) protocol + Model Context Protocol (MCP) are emerging standards. |
| 31 | "Multi-Agent Systems Transform Enterprise AI in 2026" | Shakudo / Gartner (Jan 2026) | Market projected $7.55B (2025) → $199B (2034). 40% of projects will fail by 2027. |
| 32 | "Best NL2SQL Tools 2026" | InfiniSynapse (May 2026) | 7 tools ranked across 6 dimensions. Vanna wins open-source. InfiniSynapse wins multi-source. |
| 33 | "Natural Language to SQL: The Complete 2026 Guide" | BlazeSQL (Feb 2026) | Context eats syntax for breakfast. Three pillars: business context, governance, iteration. |

---

## 4. Inference & Hardware Documentation

| # | Document | Source | Key Insight |
|---|----------|--------|-------------|
| 34 | "SGLang on AMD Cloud for LLM Inference" | AMD Developer Cloud (May 2026) | SGLang recommended for agent workloads on AMD. Day-one DeepSeek support. |
| 35 | "vLLM Inference on ROCm" | AMD ROCm Documentation (Feb 2026) | Production-grade ROCm support. Prebuilt Docker image available. |
| 36 | "SGLang Inference Performance Testing" | AMD ROCm Documentation (Feb 2026) | DeepSeek-R1-Distill-Qwen-32B on MI300X: validated performance. |
| 37 | "llama.cpp on ROCm" | AMD ROCm LLMExt (Feb 2026) | CPU-first inference with ROCm GPU acceleration. Multiple quantization options. |
| 38 | "vLLM on ROCm Setup Guide" | GigaGPU (Apr 2026) | MI300X: production. Consumer GPUs: supported. ROCm 6.3+ required for FP8. |
| 39 | "A Comprehensive Comparison of LLM Inference Engines" | N1N (Mar 2026) | TGI deprecated. vLLM for general production. SGLang for agents. TensorRT-LLM for max throughput (NVIDIA only). |
| 40 | "vLLM vs Ollama vs llama.cpp vs SGLang" | VRLA Tech (Jun 2026) | SGLang: best for structured JSON + agent tool-use. vLLM: standard for multi-user serving. |
| 41 | "Vector Database Comparison for RAG" | Lushbinary (May 2026) | Qdrant leads on filtered search and self-hosted cost-efficiency. |
| 42 | "Vector Database Performance Benchmarks 2025" | Inductivee (Apr 2026) | Qdrant: 42K vec/s insert, 18ms p99 latency, ~$280/mo at 100M vectors. |
| 43 | "Best Vector Databases 2026" | Internative (Jun 2026) | pgvector: best <10M vectors. Qdrant: best raw performance. Milvus: best >1B vectors. |
| 44 | "Vector Database Performance: pgvector vs Qdrant vs Milvus" | Culpur (Apr 2026) | pgvector (HNSW): 8ms p50, 287ms p99 at 100 QPS. Degrades at high concurrency. |

---

## 5. Market Research & Industry Analysis

| # | Report | Source | Key Insight |
|---|--------|--------|-------------|
| 45 | "Multiagent Systems: A New Era in AI-Driven Enterprise Automation" | Gartner (2026) | 1,445% surge in multi-agent inquiries from Q1 2024 to Q2 2025. |
| 46 | "Enterprise AI and Data Architecture 2025" | Cloudera (Sep 2025) | Enterprises moving from experimentation to integration. AI orchestration is key. |
| 47 | "7 Career-Making AI Decisions for CIOs in 2026" | Dataiku / Harris Poll (2026) | 74% of CIOs regret at least one major AI vendor selection in past 18 months. |
| 48 | "Intelligent Digital Brain Architecture" | Accenture (Jun 2026) | Five connected layers: data foundation → language → memory → reasoning → orchestration. |
| 49 | "Best Open-Source Semantic Layer Tools in 2026" | Level Up Coding (Mar 2026) | Cube (most mature), MetricFlow/dbt (metric computation), Malloy (experimental). |
| 50 | "Semantic Layer vs Text-to-SQL: When to Use Each" | Semantic.io (Mar 2026) | Semantic layer: 95-100% accuracy for modeled. Text-to-SQL: 60-75% for ad hoc. |
| 51 | "GraphRAG and Knowledge Graphs in 2026" | Datalinkk (Mar 2026) | GraphRAG: 40% better accuracy, 60% hallucination reduction vs pure RAG. |
| 52 | "Knowledge Graphs + LLMs: GraphRAG Beats Pure RAG" | AppScale Blog (Apr 2026) | Multi-hop reasoning is the killer app for GraphRAG. |
| 53 | "Graphwise: New GraphRAG Solution" | PRNewswire (Feb 2026) | Semantic Metadata Control Plane: 60% → 90%+ accuracy. SKOS-style concept enrichment. |
| 54 | "Top 10 Natural Language to SQL Tools in 2026" | Basedash (Feb 2026) | Seek AI: best for governed enterprise NL2SQL. $50K+/yr pricing. |
| 55 | "Snowflake vs Databricks: $36K vs $28K/Year" | Tech Insider (Jun 2026) | Snowflake: $4.68B FY2026 revenue. Databricks: $5.4B ARR (65% growth). |
| 56 | "Cost Models for NL2SQL Systems" | Engineered Insight (Mar 2026) | DB compute + human review = majority of per-query cost. |

---

## 6. Open-Source Project Repositories

| # | Project | Stars | License | Architecture | URL |
|---|---------|-------|---------|-------------|-----|
| 57 | Vanna AI | ~22K | MIT | RAG-first, self-learning | github.com/vanna-ai/vanna |
| 58 | WrenAI | ~14K | Apache 2.0 | Semantic model + engine | github.com/Canner/WrenAI |
| 59 | DB-GPT | ~17K | MIT | Multi-agent, AWEL workflow | github.com/eosphoros-ai/DB-GPT |
| 60 | SQLCoder | ~4K | Apache 2.0 | Fine-tuned 7B/15B SQL models | github.com/defog-ai/sqlcoder |
| 61 | LangGraph | ~10K | MIT | DAG-based agent orchestration | github.com/langchain-ai/langgraph |
| 62 | Qdrant | ~22K | Apache 2.0 | Rust vector database | github.com/qdrant/qdrant |
| 63 | vLLM | ~45K | Apache 2.0 | LLM inference engine | github.com/vllm-project/vllm |
| 64 | SGLang | ~8K | Apache 2.0 | Structured generation LLM engine | github.com/sgl-project/sglang |
| 65 | llama.cpp | ~75K | MIT | CPU-first LLM inference | github.com/ggml-org/llama.cpp |
| 66 | Cube | ~18K | MIT | Open-source semantic layer | github.com/cube-js/cube |
| 67 | FalkorDB | ~5K | BSD | Graph database for Text2SQL | github.com/FalkorDB/QueryWeaver |
| 68 | NL2SQL Handbook | — | MIT | Comprehensive NL2SQL survey repo | github.com/HKUSTDial/NL2SQL_Handbook |

---

## 7. Benchmark & Evaluation Sources

| # | Benchmark | Metric | Current SOTA | URL |
|---|-----------|--------|-------------|-----|
| 69 | Spider 1.0 | Execution Accuracy | 85-92% | yale-lily.github.io/spider |
| 70 | Spider 2.0 | Task Success Rate | 17.1% (o1-preview) | spider2-sql.github.io |
| 71 | BIRD | Execution Accuracy | 60-76% | bird-bench.github.io |
| 72 | LiveSQLBench | Execution Accuracy | Emerging (2026) | livesqlbench.ai |
| 73 | ANN-Benchmarks | Recall / QPS | Qdrant leads filtered search | ann-benchmarks.com |

---

## Citation Index

Documents referencing each source:

| Source ID | Referenced In |
|-----------|---------------|
| 01 | TLR §2.2, §2.3, §6.4 |
| 02 | TLR §9 (header), Bibliography |
| 03 | TLR §4.2 |
| 04 | TLR §2.3 |
| 05 | TLR §2.2, §7.3 |
| 06 | TLR §2.2 |
| 09 | TLR §13.1 |
| 10 | TLR §13.1 |
| 11 | TLR §2.1, §3.1 |
| 14 | TLR §2.1, §12.1 |
| 17 | TLR §2.1, §6.4 |
| 19 | TLR §5.3 |
| 21 | TLR §2.2, §13.1 |
| 22 | TLR §7.2 |
| 23 | TLR §3.1 |
| 34 | TLR §10.2 |
| 35 | TLR §10.1 |
| 36 | TLR §10.2 |
| 37 | TLR §10.1 |
| 39 | TLR §10.1 |
| 41 | TLR §5 (TR) |
| 42 | TLR §5 (TR) |
| 45 | TLR §2.2, §6.1 |
| 48 | TLR §17 |
| 49 | TLR §5.1 (TR) |
| 51 | TLR §8.2 |
| 55 | TLR §13.4 |
| 56 | TLR §9.3 |

**Key**: TLR = Technical Landscape Report, TR = Technology Recommendations

---

## Note on Currency

This bibliography was compiled in July 2026. The NL2SQL and AI infrastructure fields evolve rapidly. Key sources that may become outdated:

- **Inference benchmarks** (sources 39-44): 6-12 month relevance
- **Model performance** (sources 1, 5, 6): 3-6 month relevance
- **Competitive analysis** (sources 9-13): 6-12 month relevance
- **Open-source project stats** (sources 57-67): GitHub stars change continuously
- **Market projections** (sources 45, 46): Annual review recommended

Re-benchmark critical numbers before making final architectural decisions.
