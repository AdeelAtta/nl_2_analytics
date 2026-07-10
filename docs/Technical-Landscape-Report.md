# Technical Landscape Report

**Enterprise Data Intelligence Platform — Phase 0 Discovery**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 0.1 |
| **Classification** | Internal — Strategy & Architecture |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State of Enterprise Text-to-SQL](#2-current-state-of-enterprise-text-to-sql)
3. [Enterprise Pain Points](#3-enterprise-pain-points)
4. [Schema Adaptation Techniques](#4-schema-adaptation-techniques)
5. [Semantic Modeling & Knowledge Layer Approaches](#5-semantic-modeling--knowledge-layer-approaches)
6. [Multi-Agent Architectures](#6-multi-agent-architectures)
7. [RAG and Hybrid Retrieval Strategies](#7-rag-and-hybrid-retrieval-strategies)
8. [Knowledge Graphs & Ontologies](#8-knowledge-graphs--ontologies)
9. [LLM Comparison](#9-llm-comparison)
10. [Inference Frameworks & Deployment Options](#10-inference-frameworks--deployment-options)
11. [Database Connectivity & SQL Dialects](#11-database-connectivity--sql-dialects)
12. [Security & Governance Requirements](#12-security--governance-requirements)
13. [Competitive Landscape](#13-competitive-landscape)
14. [Research Gaps & Market Opportunities](#14-research-gaps--market-opportunities)
15. [Technology Trade-offs](#15-technology-trade-offs)
16. [Recommended Technology Stack](#16-recommended-technology-stack)
17. [Recommended Product Architecture](#17-recommended-product-architecture)
18. [Technical Risks](#18-technical-risks)
19. [Open Research Questions](#19-open-research-questions)
20. [Final Recommendations](#20-final-recommendations)

---

## 1. Executive Summary

### The Problem

Enterprise data access is broken. Business users who need data cannot write SQL. Data analysts spend 40-60% of their time writing routine queries instead of doing high-value analysis. The result: slow decision-making, bottlenecked data teams, and millions in lost productivity.

Natural Language to SQL (NL2SQL) promises to solve this, but current solutions fail in production. The industry faces a critical gap:

| Benchmark | Accuracy | What It Tests |
|-----------|----------|---------------|
| Spider 1.0 | 85-92% | Clean academic schemas, 3-10 tables |
| BIRD | 60-76% | Messy real-world data, 95 databases |
| **Spider 2.0** | **6-21%** | Enterprise workflows, 1000+ columns, real BigQuery/Snowflake |
| **Enterprise Production** | **10-40%** | Actual customer environments with poor documentation |

The gap between academic benchmarks (85%+) and enterprise production (<21%) is not a model problem — it is an **architecture problem**.

### The Opportunity

After analyzing 50+ sources including academic papers (Spider 2.0, BIRD, LitE-SQL), enterprise products (Snowflake Cortex Analyst, Databricks Genie, Oracle OCI NL2SQL), open-source projects (Vanna AI, WrenAI, DB-GPT), and industry analysis (Gartner, Accenture, dbt Labs), the key findings are:

1. **The semantic layer is the bottleneck.** Every serious solution requires manual YAML/configuration to define business meaning. No vendor has solved autonomous semantic discovery.

2. **Multi-agent architectures are the proven paradigm.** Systems using decomposed agent pipelines (planner → schema linker → generator → validator → reflector) consistently outperform single-shot approaches by 15-30%.

3. **Warehouse-native solutions are insufficient.** Snowflake Cortex Analyst, Databricks Genie, and BigQuery Gemini only work within their own ecosystem. Multi-database enterprises must stitch together multiple tools.

4. **The RAG + semantic model + graph hybrid is emerging.** The best production systems combine vector retrieval (for schema examples), structured semantic models (for business definitions), and knowledge graphs (for relationship traversal).

5. **AMD ROCm ecosystem has matured.** vLLM, SGLang, and llama.cpp all have production-grade ROCm support. The GPU architecture gap is narrowing.

### The Recommendation

Build an **Autonomous Context Layer** platform that:

- Reverse-engineers business meaning from schemas, query history, and documentation
- Provides cross-database NL2SQL with enterprise governance
- Self-improves through a continuous learning loop
- Deploys on AMD ROCm as the primary inference target
- Remains hardware-agnostic through an inference abstraction layer

This is the market gap. No existing product — open-source or commercial — delivers autonomous semantic discovery at enterprise scale.

---

## 2. Current State of Enterprise Text-to-SQL

### 2.1 The NL2SQL Pipeline (Consensus Architecture)

Modern NL2SQL systems follow a multi-stage pipeline. This is the industry consensus, validated across Oracle OCI, AWS, Snowflake, Databricks, and all major open-source projects:

```
User Question
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Intent Classification            │  ← Is this a data question?
│    & Input Sanitization             │  ← Strip injection attacks
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 2. Schema Retrieval & Linking       │  ← Find relevant tables/columns
│    (Vector search + metadata)       │  ← Prune to manageable context
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 3. Context Assembly                 │  ← DDL + business docs + examples
│    (Prompt construction)            │  ← Historical Q&A retrieval
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 4. SQL Generation                   │  ← LLM produces candidate SQL
│    (Multi-candidate sampling)       │  ← Temperature-based diversity
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 5. Validation & Execution           │  ← Syntax check, dry-run, RBAC
│    (Deterministic guardrails)       │  ← Cost ceiling enforcement
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 6. Reflection & Repair              │  ← Self-critique if results
│    (Iterative improvement loop)     │  ← suspicious or empty
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 7. Explanation & Visualization      │  ← Natural language summary
│    (Results presentation)           │  ← Auto-generated charts
└─────────────────────────────────────┘
```

**Source**: Oracle OCI NL2SQL whitepaper, AWS/Cisco enterprise NL2SQL blog, InfiniSynapse NL2SQL guide, N1N 7-layer guardrail stack.

### 2.2 Key Research Findings (2025-2026)

| Finding | Source | Implication |
|---------|--------|-------------|
| Pre-computed schema embeddings + contrastive learning achieve 88.45% on Spider with 2-30x fewer parameters | LitE-SQL (EACL 2026) | Schema indexing is more efficient than per-request embedding |
| RAG with examples beats semantic models and multi-step pipelines in head-to-head benchmarks | Sudipta Pathak (Feb 2026) benchmark: Vanna 40% vs WrenAI 22% vs DB-GPT 20% | Context quality matters more than pipeline complexity |
| Spider 2.0: Even o1-preview solves only 17.1% of enterprise tasks | Spider 2.0 paper (ICLR 2025 Oral) | Enterprise NL2SQL is fundamentally unsolved |
| Semantic Layer approaches 100% accuracy for well-modeled queries | dbt Labs 2026 benchmark | Deterministic query generation through structured ontologies is the gold standard |
| GraphRAG reduces hallucinations by 60% vs pure RAG on complex queries | Zylos AI / Datalinkk (Feb 2026) | Knowledge graphs are essential for multi-hop enterprise reasoning |
| HuggingFace TGI moved to maintenance mode (March 2026) | HuggingFace announcement | Industry consolidating around vLLM and SGLang |
| vLLM, SGLang, and llama.cpp all support AMD ROCm in production | AMD ROCm documentation (2026) | AMD is a viable inference target |

### 2.3 The Benchmark-to-Production Gap

This gap is the most important finding in this report. The numbers:

| Benchmark | Year | Best Accuracy | Characteristics |
|-----------|------|---------------|-----------------|
| WikiSQL | 2019 | 90%+ | Single table, simple questions |
| Spider 1.0 | 2023 | 85-92% | Multiple tables, clean names, known schema |
| BIRD | 2024 | 60-76% | Dirty data, large databases, external knowledge |
| Spider 2.0 | 2025 | **6-21%** | 1000+ columns, real cloud DBs, multi-dialect |
| Production (reported) | 2026 | **10-40%** | Actual enterprise environments |

**The drop from 85% to 21% is not caused by worse models. It is caused by:**

1. **Schema complexity**: Enterprise schemas have 100-10,000+ tables with cryptic names
2. **Missing context**: Business meaning is not in the DDL
3. **Multi-hop relationships**: Questions require 4-7 table joins through indirect paths
4. **Domain-specific terminology**: "MOC 3" means "Monthly Operating Cycle 3" to one company
5. **Stale metadata**: Column comments are often empty or outdated

**Source**: Spider 2.0 paper (arXiv:2411.07763), InfiniSynapse NL2SQL guide, LinkedIn Engineering blog.

---

## 3. Enterprise Pain Points

### 3.1 The Four Recurring Failure Modes

Oracle OCI's research team identified four root causes of enterprise NL2SQL failure. This analysis is independently corroborated by AWS/Cisco and multiple production case studies:

#### Failure Mode 1: Ambiguous User Intent

> "How did OCI do last month?"

- "OCI" may refer to an organization, a campaign, or a region
- "Do" may imply revenue, margin, bookings, or YoY growth
- "Last month" may depend on data refresh cutoffs, fiscal calendars, and user-specific rules

**Resolution required**: Intent disambiguation + role-aware defaults + temporal semantics

#### Failure Mode 2: Missing Business Knowledge

Terms like "healthy growth accounts" or "North Europe" represent internal definitions, threshold rules, and org mappings that are never expressed as clean table or column names.

**Resolution required**: Business knowledge layer that captures metric definitions, hierarchies, and policies

#### Failure Mode 3: Physical Schema Complexity

Two warehouses can represent the same analytical concept differently:
- `revenue + currency_code` vs materialized `revenue_usd`
- Refunds as negative facts vs explicit adjustment rows
- Nested/embedded structures (XML strings, JSON blobs)

**Resolution required**: Schema intelligence that understands physical modeling patterns

#### Failure Mode 4: Context Sensitivity

> "This month's pipeline conversion for my region"

Changes meaning based on: current date, data freshness, user identity, geography mapping, reporting locale.

**Resolution required**: Context-aware execution with user-specific defaults

**Source**: Oracle OCI NL2SQL blog (Sujeeth Bharadwaj, Tao Sheng, Dan Roth, Sujith Ravi).

### 3.2 Enterprise Survey Data

| Statistic | Source |
|-----------|--------|
| 68% of enterprise data goes unanalyzed due to silos | IBM |
| $12.9M average annual loss per enterprise from poor data quality | Gartner |
| 40-60% of analyst time spent on routine SQL queries | Multiple industry surveys |
| 74% of CIOs regret at least one major AI vendor selection in past 18 months | Dataiku/Harris Poll 2026 |
| <2% of enterprises have deployed agentic AI at full production scale | Ampcome/Gartner 2026 |

---

## 4. Schema Adaptation Techniques

### 4.1 The Schema Challenge

Enterprise schemas are optimized for storage, not retrieval. Key problems:

- **Cryptic naming**: `c1_x7f9`, `dim_fct_sls_trx_hist`, `TBL_ACCT_BAL_202407`
- **Missing foreign keys**: Relationships are implicit, not declared
- **Denormalized structures**: Star schemas, snowflakes, wide tables with 500+ columns
- **Nested data**: XML, JSON, ARRAY columns that require unnesting
- **Shadow tables**: Multiple versions of the same logical table

### 4.2 Techniques by Maturity

| Technique | Maturity | Effectiveness | Complexity |
|-----------|----------|---------------|------------|
| DDL embedding + vector search | Production | 70-85% recall | Low |
| Query history mining | Production | 80-90% for common patterns | Medium |
| LLM-based column description generation | Production | 60-75% accuracy | Medium |
| Foreign key inference from query logs | Emerging | 50-70% precision | High |
| Active learning (human feedback loop) | Production | Improves over time | Medium |
| Schema profiling (data type detection) | Production | 90%+ for basic types | Low |
| Value distribution analysis | Emerging | Helpful for enum detection | Medium |
| Cross-database schema matching | Research | 30-50% accuracy | Very High |

### 4.3 Recommendation

**Approach**: Hybrid schema indexing combining pre-computed DDL embeddings (LitE-SQL approach) with query-history-based relationship discovery.

**Rationale**: LitE-SQL achieves 88.45% on Spider with 2-30x fewer parameters by pre-computing schema embeddings with contrastive learning. Query history mining (used by Vanna's self-learning loop) adds the second dimension of real usage patterns.

**Rejected alternative**: Full-schema prompting. This fails beyond ~100 tables due to context window limits and increased hallucination rates.

---

## 5. Semantic Modeling & Knowledge Layer Approaches

### 5.1 Landscape Overview

There are three dominant approaches to semantic modeling for NL2SQL:

| Approach | Example | Philosophy | Strengths | Weaknesses |
|----------|---------|------------|-----------|------------|
| **Manual Semantic Model** | Snowflake Cortex Analyst (YAML), WrenAI (MDL), dbt Semantic Layer | Human experts define metrics, dimensions, relationships | Near-100% accuracy for modeled queries | Weeks to months to model; doesn't scale to 1000+ tables |
| **RAG-based Context** | Vanna AI (DDL + docs + Q&A pairs), LlamaIndex | Retrieve relevant context at query time | No upfront modeling; adapts automatically | Inconsistent accuracy; no governance |
| **Autonomous Discovery** | Myriade (reverse-engineers context), Promethium | AI auto-generates semantic layer from schemas | Fast (hours vs weeks); discovers hidden relationships | Lower initial accuracy; requires human validation |

### 5.2 The Market Gap

**No product today combines autonomous discovery with production-grade NL2SQL.**

- Myriade generates documentation autonomously (72h for 150+ tables) but does not generate SQL
- Vanna generates SQL but requires manual training data curation
- WrenAI has a strong semantic model but requires manual MDL authoring
- Snowflake/Databricks have governed NL2SQL but require manual YAML and are warehouse-locked

**This is our primary product opportunity.**

### 5.3 dbt Labs 2026 Benchmark (Critical Finding)

dbt Labs ran a head-to-head benchmark comparing Text-to-SQL vs Semantic Layer approaches:

| Approach | Accuracy (modeled queries) | Accuracy (ad hoc queries) | Setup Time |
|----------|---------------------------|---------------------------|------------|
| Raw Text-to-SQL (GPT-4o) | 45-60% | 60-70% | Minutes |
| Semantic Layer (dbt + MetricFlow) | **95-100%** | 40-55% | Weeks |
| Minimal modeling + Text-to-SQL | 65-80% | 65-75% | Hours |
| Text-to-SQL with RAG context | 70-85% | 70-80% | Days |

**Key insight**: Adding even minimal modeling on top of raw tables improved results across the board. The Semantic Layer is the accuracy ceiling, but Text-to-SQL with RAG is the flexibility winner.

**Our strategy**: Combine both — use autonomous discovery to generate a semi-structured semantic model, then use RAG to augment with examples and documentation. This gives near-SL accuracy with no manual setup.

**Source**: dbt Labs Developer Blog, "Semantic Layer vs. Text-to-SQL: 2026 Benchmark Update" (April 7, 2026).

---

## 6. Multi-Agent Architectures

### 6.1 Current State

Multi-agent architectures are the dominant paradigm for production NL2SQL in 2026. Gartner reports a **1,445% surge** in multi-agent inquiries from Q1 2024 to Q2 2025.

The key insight: decomposing the NL2SQL problem into specialized agent roles consistently outperforms monolithic prompting by 15-30%.

### 6.2 Open-Source Multi-Agent Frameworks

| Framework | Stars | Language | Key Strength | NL2SQL Suitability |
|-----------|-------|----------|-------------|-------------------|
| **LangGraph** | 10k+ | Python | DAG-based orchestration, cycles, conditional branching | High — best for complex NL2SQL pipelines |
| **CrewAI** | 25k+ | Python | Role-based agent teams, simple API | Medium — good for simple pipelines |
| **AutoGen** | 35k+ | Python | Multi-agent conversation, code generation | Medium-High — strong for code generation |
| **DB-GPT** | 17k+ | Python | AWEL workflow engine, built-in NL2SQL | High — purpose-built for database agents |
| **Semantic Kernel** | 22k+ | C#/Python | Microsoft, enterprise features | Medium — strong orchestration |

### 6.3 Agent Roles for NL2SQL

The industry consensus (validated across Cisco, Oracle, AWS, and open-source projects) identifies these agent roles:

| Agent | Responsibility | Model Type | Decision |
|-------|---------------|------------|----------|
| **Planner/Classifier** | Intent detection, query decomposition | Fast/cheap model | Is this a data question? What sub-tasks needed? |
| **Schema Retriever** | Table/column selection, relationship discovery | Embedding + lightweight model | Which tables are relevant? |
| **Business Context Agent** | Business term resolution, metric definition | RAG over knowledge base | What does "revenue" mean? |
| **SQL Generator** | SQL query generation | Frontier model | Produce candidate SQL |
| **Validator** | Syntax check, security scan, cost estimation | Deterministic + LLM judge | Is the SQL safe and correct? |
| **Reflector/Repairer** | Self-critique, iterative fix | Frontier model | Can we fix the SQL? |
| **Learner** | Feedback ingestion, training data generation | Pipeline | What did we learn from this query? |

### 6.4 The Two Key Research Papers

1. **LitE-SQL (EACL 2026)**: Pre-computed schema embeddings with contrastive learning. 88.45% on Spider, 72.10% on BIRD. 2-30x fewer parameters than full LLM approaches. **Key insight: schema context should be indexed, not generated per request.**

2. **Spider 2.0 Agent Framework (ICLR 2025)**: Code agent framework that solves 21.3% of tasks (vs 10.1% for GPT-4o). Uses multi-step tool use, dialect documentation search, and iterative refinement. **Key insight: agents need access to dialect documentation, not just schema.**

### 6.5 Recommendation

Use **LangGraph** as the primary agent orchestration framework with 5-7 specialized agents.

**Rationale**: LangGraph's DAG + cycle support maps directly to the NL2SQL pipeline (plan → retrieve → generate → validate → repair → learn). It has the most mature production ecosystem (LangSmith for observability, LangServe for deployment) and supports conditional branching for error handling.

**Alternative considered**: CrewAI (simpler but less flexible for complex pipelines), DB-GPT (purpose-built but less supported outside China).

---

## 7. RAG and Hybrid Retrieval Strategies

### 7.1 Current Best Practices

2026 has seen convergence on best practices for RAG in NL2SQL:

| Strategy | Description | Effectiveness | When to Use |
|----------|-------------|---------------|-------------|
| **DDL Vector Store** | Pre-compute embeddings of all DDL statements | High recall, low latency | Schema >100 tables |
| **Question-SQL Pair Store** | Store successful Q&A pairs for future retrieval | Improves over time | After launch (needs data) |
| **Documentation Store** | Embed business docs, wikis, knowledge base | Medium (depends on quality) | When docs exist |
| **Query History Index** | Index past SQL queries with descriptions | High for common patterns | Mature deployments |
| **Hybrid Search (Vector + Keyword)** | Combine ANN with BM25/keyword | Higher recall than either alone | All production deployments |
| **Multi-hop Retrieval** | Retrieve, then refine based on initial results | 3-5x better on complex queries | Complex analytical questions |
| **Graph-based Retrieval** | Traverse entity relationships | Best for multi-join queries | When relationships matter |

### 7.2 The Vanna AI Approach (Validated)

Vanna AI's RAG-first architecture was benchmarked at **40% execution accuracy** vs 22% (WrenAI) and 20% (DB-GPT) on a 50-query test with the same LLM (GPT-4o). Vanna's advantage:

1. **Self-learning loop**: Successful query-SQL pairs are automatically added back to the training set
2. **Two-pass generation**: First pass generates initial SQL; second pass inspects actual data before finalizing
3. **Minimal infrastructure**: Single pipeline with vector store + LLM

**Source**: Sudipta Pathak, "NL2SQL Benchmark: Vanna AI vs WrenAI vs DB-GPT" (Feb 2026).

### 7.3 The Pre-computed Embedding Advantage

LitE-SQL demonstrated that pre-computing schema embeddings with contrastive learning outperforms per-request embedding generation:

| Metric | Per-Request Embedding | Pre-computed (LitE-SQL) |
|--------|----------------------|------------------------|
| Spider accuracy | ~82% | 88.45% |
| BIRD accuracy | ~65% | 72.10% |
| Inference cost | Higher (redundant) | Lower (cached) |
| Schema change handling | Immediate | Requires re-index |

**Recommendation**: Pre-compute and cache all schema embeddings. Update on schema changes (DDL events). This is the approach used by both LitE-SQL and Vanna AI.

### 7.4 When Each Strategy Fails

| Strategy | Failure Mode | Mitigation |
|----------|--------------|------------|
| DDL-only | Cryptic names, no business context | Augment with documentation |
| Documentation-only | Outdated docs, missing coverage | Combine with query history |
| Query history-only | Cold start problem, rare patterns | Bootstrap with DDL |
| Vector-only | Misses exact keyword matches | Hybrid vector + keyword |
| Single-hop | Fails on multi-join questions | Multi-hop retrieval chain |

---

## 8. Knowledge Graphs & Ontologies

### 8.1 Why Knowledge Graphs Matter for NL2SQL

Pure vector RAG retrieves semantically similar chunks but cannot traverse relationships. For enterprise questions like "What suppliers serve customers in the Northeast region who ordered product category X?", the system needs to follow a chain of relationships — which vector search cannot do.

**GraphRAG addresses this**: by modeling entities (tables, columns, metrics, business terms) as nodes and their relationships as edges, graph traversal finds information that semantic search misses.

### 8.2 Research Validation

| Study | Finding | Source |
|-------|---------|--------|
| Zylos AI (Feb 2026) | 40% better accuracy on complex queries, 60% hallucination reduction | Enterprise GraphRAG report |
| 47Billion (Mar 2026) | Graph RAG reduces legal reasoning errors by 30-40% over pure RAG | Legal AI benchmark |
| Datalinkk (Mar 2026) | Graph traversal finds info that vector search cannot for multi-hop queries | Production case study |
| StackViv (Jul 2026) | Microsoft's GraphRAG (local-to-global) is the reference architecture | 2026 Guide |

### 8.3 Knowledge Graph Architectures for NL2SQL

| Architecture | Description | Best For |
|-------------|-------------|----------|
| **Microsoft GraphRAG** | Hierarchical community detection + local/global search | Document understanding for BI context |
| **Text2Cypher** | LLM generates graph queries from NL | Flexible, no predefined paths |
| **Metadata Graph** | Models tables, columns, metrics as nodes | Schema mapping + business term resolution |
| **Entity Resolution Graph** | Links business terms to physical schema columns | Semantic enrichment |
| **Agent-Based GraphRAG** | Agents traverse graph as a tool | Complex multi-step analytical queries |

### 8.4 Recommendation

**Do not build a full GraphRAG system for Phase 1.** Instead, use a lightweight "Metadata Knowledge Graph" that models:

- Tables → relationships (foreign keys, query-implied joins)
- Business terms → columns (mappings discovered from docs)
- Metrics → definitions (measurement formulas)
- Users → role-based schema access

This can be stored in a graph database (Neo4j or FalkorDB) or even as structured metadata on top of the vector store.

**Full GraphRAG** should be added in Phase 2-3 when multi-hop analytical queries become critical.

---

## 9. LLM Comparison

### 9.1 Model Landscape (Mid-2026)

| Model | Type | Context | NL2SQL Quality | Cost/Tok | Self-Hostable | ROCm Support |
|-------|------|---------|----------------|----------|---------------|--------------|
| **GPT-4o** | Commercial | 128K | Excellent | High | No | N/A |
| **Claude 3.5 Sonnet** | Commercial | 200K | Excellent | High | No | N/A |
| **Claude 3 Opus** | Commercial | 200K | Best-in-class | Very High | No | N/A |
| **Gemini 2.0 Pro** | Commercial | 1M+ | Very Good | Medium | No | N/A |
| **DeepSeek-V3** | Open | 128K | Very Good | Low | Yes | Yes (SGLang) |
| **DeepSeek-R1** | Open | 128K | Excellent (reasoning) | Medium | Yes | Yes (SGLang) |
| **Qwen2.5-72B** | Open | 128K+ | Good | Low | Yes | Yes (vLLM) |
| **Llama 4** | Open | 1M+ | Good | Low | Yes | Yes (vLLM) |
| **SQLCoder-7b-2** | Open | 32K | Excellent on SQL | Very Low | Yes | Yes |
| **Defog SQLCoder 15B** | Open | 32K | Best open for SQL | Low | Yes | Yes |
| **Mistral Large 2** | Open/API | 128K | Good | Medium | Yes | Yes |
| **Mixtral 8x22B** | Open | 128K | Good | Low | Yes | Yes |

### 9.2 SQL-Specific Models

| Model | Spider | BIRD | Notes |
|-------|--------|------|-------|
| SQLCoder-7b-2 | 91.4% (ratio) | — | Outperforms GPT-4 on complex ratio queries |
| Defog SQLCoder 15B | 87.6% | — | Best general-purpose SQL model |
| BIRD-Talon-14B | — | 65%+ | RL-trained from BIRD benchmark |
| BIRD-Zeno-7B | — | 60%+ | Smaller, faster alternative |
| GPT-4o (zero-shot) | 85-92% | 60-70% | Strong without fine-tuning |

### 9.3 The Inference Cost Equation

For a production NL2SQL system processing 10,000 queries/day:

| Scenario | Model | Monthly Inference Cost |
|----------|-------|----------------------|
| Cloud API | GPT-4o (all queries) | $15,000-30,000 |
| Cloud API | GPT-4o (25%) + GPT-4o-mini (75%) | $5,000-10,000 |
| Self-hosted | DeepSeek-V3 + Qwen 7B router | $2,000-5,000 (GPU amortized) |
| Self-hosted | SQLCoder-7b + Llama 4 | $1,000-3,000 (GPU amortized) |
| Edge/Local | SQLCoder-7b (quantized) | $300-500 (hardware cost) |

**Recommendation**: Tiered inference strategy:
- **Fast path** (~70% of queries): SQLCoder-7b or Qwen2.5-7B for simple queries
- **Complex path** (~25%): DeepSeek-V3 or Qwen2.5-72B for multi-join/analytical
- **Hard path** (~5%): GPT-4o/Claude 3.5 API for edge cases, followed by fine-tuned open model over time

### 9.4 The "Router Model" Pattern

The industry best practice (validated by AWS/Cisco, Oracle, and multiple case studies) is to use a **fast classifier/router** to dispatch to the right model:

```
Question → Classifier (Qwen2.5-7B) → Simple → SQLCoder-7b
                                      → Medium → DeepSeek-V3
                                      → Complex → GPT-4o / Claude
                                      → Off-topic → Reject with explanation
```

This reduces inference costs by **50-70%** while maintaining accuracy on complex queries.

---

## 10. Inference Frameworks & Deployment Options

### 10.1 Framework Comparison (Mid-2026)

| Framework | License | Hardware | Throughput | Best For | ROCm Support |
|-----------|---------|----------|------------|----------|--------------|
| **vLLM** | Apache 2.0 | GPU | 1000-2000 tok/s | General production serving | Yes (production) |
| **SGLang** | Apache 2.0 | GPU | Very high | Structured output, agents, RAG | Yes (production) |
| **llama.cpp** | MIT | CPU/GPU/Edge | 80-100 tok/s | Local/edge/quantized inference | Yes (ROCm/LLMExt) |
| **Ollama** | MIT | Cross-platform | Low-Med | Fast prototyping, single user | Yes |
| **TensorRT-LLM** | Apache 2.0 | NVIDIA only | 2500-4000 tok/s | Maximum throughput (NVIDIA) | No |
| **TGI** | Apache 2.0 | GPU | 800-1500 tok/s | Deprecated (maintenance mode) | Limited |

**Key changes in 2026**:
- HuggingFace TGI moved to maintenance mode (March 2026)
- AMD ROCm support is now production-grade for vLLM, SGLang, and llama.cpp
- SGLang has emerged as the preferred engine for agent workloads (structured output, tool use)
- vLLM v1 engine added native AMD Instinct support

### 10.2 AMD Hardware Options

| GPU | Architecture | VRAM | Bandwidth | vLLM Status | SGLang Status | Best For |
|-----|-------------|------|-----------|-------------|---------------|----------|
| MI300X | CDNA3 | 192 GB HBM3 | 5.3 TB/s | Production | Production | Large models, high throughput |
| MI325X | CDNA3 | 288 GB HBM3 | 6.0 TB/s | Production | Production | Largest models |
| MI350X | CDNA4 | 288 GB HBM3e | — | Production | Production | Next-gen inference |
| RX 7900 XTX | RDNA3 | 24 GB | 960 GB/s | Supported | Supported | Small models, dev/test |
| RX 9070 XT | RDNA4 | 16 GB | 640 GB/s | Supported (Triton) | Supported | Edge, development |

### 10.3 Deployment Architecture Options

| Architecture | Latency | Throughput | Cost | Complexity | Best For |
|-------------|---------|------------|------|------------|----------|
| Single GPU (MI300X) | 50-200ms | 50 QPS | $ | Low | MVP, low-moderate load |
| Multi-GPU (2-8x MI300X) | 30-100ms | 200-1000 QPS | $$ | Medium | Production, moderate load |
| Multi-Node (Kubernetes) | 30-80ms | 1000+ QPS | $$$ | High | Enterprise, high load |
| Cloud API Fallback | 500-2000ms | Unlimited | $$$$ | Low | Burst, complex queries |

### 10.4 Recommendation

**Inference Engine**: vLLM for production serving (general inference), SGLang for agent/structured-output workloads. Both have ROCm support.

**Target Hardware**: AMD MI300X (192 GB) for initial production. Single node with 4-8 GPUs for MVP scale.

**Abstraction Layer**: Build a lightweight inference provider abstraction:

```python
class InferenceProvider:
    def __init__(self, provider_type: str, config: dict):
        # provider_type: "vllm", "sglang", "openai", "anthropic", "ollama"
        ...
    
    async def generate(
        self, 
        model: str, 
        messages: list, 
        temperature: float = 0.1,
        structured_output: Optional[Type] = None
    ) -> str:
        ...
```

This allows switching between self-hosted AMD and cloud APIs without code changes.

---

## 11. Database Connectivity & SQL Dialects

### 11.1 Supported Dialects (Priority Order)

| Dialect | Popularity | NL2SQL Difficulty | Priority |
|---------|-----------|-------------------|----------|
| PostgreSQL | Very High | Low | P0 — MVP |
| MySQL | Very High | Low | P0 — MVP |
| Snowflake SQL | High | Medium | P0 — MVP |
| BigQuery SQL | High | Medium | P0 — MVP |
| DuckDB | Medium | Low | P0 — MVP (dev/test) |
| SQLite | Very High | Low | P1 (embedded) |
| Microsoft SQL Server | High | Medium | P1 |
| Oracle SQL | High | High | P1 |
| Amazon Redshift | High | Medium | P1 |
| ClickHouse | Medium | Medium | P2 |
| Databricks SQL | Medium | Medium | P2 |
| Apache Spark SQL | Medium | High | P2 |
| Presto/Trino | Medium | Medium | P2 |
| CockroachDB | Low | Low | P3 |
| MariaDB | Medium | Low | P3 |

### 11.2 Dialect Complexity Factors

| Factor | Impact | Example |
|--------|--------|---------|
| Function name differences | High | `DATE_TRUNC('month', col)` (Postgres) vs `DATE_TRUNC(col, 'month')` (Snowflake) |
| Data type differences | Medium | `TEXT` vs `VARCHAR` vs `STRING` |
| Window function syntax | High | `QUALIFY` (Snowflake) vs no equivalent |
| Semi-structured data | Very High | `JSONB` operators (Postgres) vs `PARSE_JSON` (Snowflake) |
| Temporary/CTE syntax | Medium | `WITH` clause differences |
| Limit/Offset syntax | Medium | `LIMIT/OFFSET` vs `FETCH FIRST ROWS ONLY` |
| String functions | High | `CONCAT` vs `||` vs `CONCAT_WS` |

### 11.3 Abstraction Strategy

**Recommended approach**: Provide the full DDL + dialect documentation to the LLM as context. Do not transpile. The LLM has sufficient knowledge of SQL dialects when given proper context.

**Rationale**: The Spider 2.0 agent framework showed that providing dialect documentation improves accuracy by 5-10%. SQL transpilation (converting between dialects) introduces additional failure modes and is unnecessary when the LLM can generate dialect-native SQL from proper context.

**Connection layer**: Use SQLAlchemy as the database abstraction layer with custom connection managers for each dialect. Each connector handles:
- Authentication (password, OAuth, IAM, SSO)
- Schema introspection (tables, columns, types, constraints)
- Query execution (read-only enforcement, timeout, result pagination)
- Metadata extraction (comments, statistics, query history)

---

## 12. Security & Governance Requirements

### 12.1 The 7-Layer Guardrail Stack

Based on the ASK-TARA system (90,000+ queries, zero security incidents), the industry consensus guardrail architecture:

| Layer | Function | Implementation |
|-------|----------|---------------|
| **L1: Intent Classification** | Block non-data queries (greetings, off-topic, injection) | Lightweight classifier + regex patterns |
| **L2: Input Sanitization** | Strip injection attacks, homoglyphs, prompt injection | Whitelist-based filtering |
| **L3: RBAC Schema Scoping** | Only expose tables/columns user has permission to access | Dynamic DDL generation per role |
| **L4: Query Cost Ceiling** | Terminate queries exceeding cost/time thresholds | Token estimation + query complexity analysis |
| **L5: SQL Validation** | Syntax check, schema conformance, no destructive operations | sqlparse + LLM judge |
| **L6: Read-Only Execution** | Execute in sandboxed, read-only transaction | Database user permissions + connection pooling |
| **L7: Audit Logging** | Log every query with user, timestamp, SQL, result hash | Structured logging + immutable audit trail |

The pipeline follows a **fail-closed** philosophy: if any layer detects an anomaly, the query is immediately terminated.

**Source**: N1N 7-layer guardrail stack, ASK-TARA production system.

### 12.2 Compliance Requirements

| Requirement | Standard | Implementation |
|-------------|----------|---------------|
| SOC 2 Type II | All enterprise customers | Access controls, audit logs, encryption at rest/in transit |
| GDPR | EU customers | Data residency, right to deletion, processing records |
| HIPAA | Healthcare | BAA, PHI access controls, audit trails |
| RBAC | All | Role-based access to schemas and features |
| Column-level security | Sensitive data | Dynamic column masking based on user role |
| Audit trail | All | Immutable, searchable query history |

### 12.3 The "Zero Data Access" Pattern

Critical insight from production deployments: **The AI system should not need direct data access to generate accurate SQL.**

WrenAI's approach (metadata-only, no data access) is the most secure pattern. The validation can be done via:
- **Dry-run validation**: Execute the SQL and check for errors, but discard results
- **Result metadata**: Return row count, column types, execution time without actual data
- **Hash-based verification**: Compare result hashes to expected patterns

Our recommendation: **Metadata-first, data-on-demand.** The context layer operates on schema metadata + query history + documentation. Actual data access is only required for validation and result presentation — and is strictly governed by RBAC.

---

## 13. Competitive Landscape

### 13.1 Competitor Tier Classification

#### Tier 1: Warehouse-Native NL2SQL

| Product | Warehouse | Semantic Model | Accuracy (Reported) | Pricing |
|---------|-----------|---------------|---------------------|---------|
| Snowflake Cortex Analyst | Snowflake only | YAML semantic model | 80-90% (Snowflake claims) | Included in Snowflake credits |
| Databricks AI/BI Genie | Databricks only | Unity Catalog + trusted assets | 75-85% | Included in Databricks DBUs |
| BigQuery Gemini | BigQuery only | Dataform views | 70-80% | Vertex AI usage + BigQuery slots |
| Microsoft Copilot for Fabric | Microsoft Fabric | Power BI semantic model | 70-80% | Fabric capacity |

**Strengths**: Zero data movement, native governance, no separate vendor
**Weaknesses**: Single-platform lock-in, manual semantic setup, limited to simple queries

#### Tier 2: Enterprise BI with NL2SQL

| Product | Approach | Accuracy | Pricing |
|---------|----------|----------|---------|
| ThoughtSpot Spotter | Proprietary search + ML | 70-80% | $100K+/yr enterprise |
| Looker + Gemini | LookML semantic model | 70-80% | Included in Google Cloud |
| Hex | Notebook + AI assistant | 60-75% | $50-150/seat/month |
| Rill | Dashboard-first with AI | 60-70% | Open-source + cloud |

**Strengths**: Mature BI capabilities, visualization, collaboration
**Weaknesses**: Heavy setup cost, limited AI autonomy, warehouse-locked

#### Tier 3: Open-Source NL2SQL Frameworks

| Project | Stars | Architecture | License | Best For |
|---------|-------|-------------|---------|----------|
| Vanna AI | 22k+ | RAG-first, self-learning | MIT | Embedding NL2SQL in custom apps |
| WrenAI | 14k+ | Semantic model + engine | Apache 2.0 | GenBI platform with governance |
| DB-GPT | 17k+ | Multi-agent, workflow-driven | MIT | Complex multi-step pipelines |
| SQLCoder | 4k+ | Fine-tuned model (not a framework) | Apache 2.0 | SQL generation backbone |

**Strengths**: Flexible, self-hostable, no per-query cost
**Weaknesses**: Requires engineering team to operate, limited out-of-box governance

#### Tier 4: Pure-Play NL2SQL Startups

| Company | Approach | Accuracy | Pricing |
|---------|----------|----------|---------|
| Seek AI | Proprietary SEEKER-1 + guardrails | 75-85% | Custom enterprise ($50K+/yr) |
| Dataherald | Open-source NL2SQL engine | 60-70% | Open-source + cloud |
| Text2SQL.ai | Browser-based utility | 50-60% | Free / $7-29/mo |
| AI2SQL | Complex SQL focus | 65-75% | $10-50/mo |
| SQLAI.ai | Cost-optimized | 60-70% | $5/mo |

### 13.2 Competitive Positioning Matrix

```
                    HIGH GOVERNANCE
                         │
                         │
     Snowflake CA ●      │      ● WrenAI
     Databricks Genie ●  │
     BigQuery Gemini ●   │
                         │
     ────────────────────┼──────────────────────
                         │
     Vanna AI ●          │      ● Our Product
     DB-GPT ●            │      (Anticipated)
     SQLCoder ●          │
     Text2SQL.ai ●       │
                         │
                    LOW GOVERNANCE
                         │
                  SINGLE-DB          MULTI-DB
```

**Our opportunity**: The upper-right quadrant (multi-database + high governance) is the least populated. WrenAI is the closest competitor but requires manual MDL authoring. Snowflake/Databricks are single-platform.

### 13.3 Key Competitive Advantages

| Competitor | Their Weakness | Our Advantage |
|------------|---------------|---------------|
| Snowflake Cortex Analyst | Manual YAML, Snowflake-only | Autonomous schema discovery, multi-DB |
| Databricks Genie | Requires Unity Catalog curation | Zero-setup schema intelligence |
| WrenAI | Manual MDL authoring (AGPL license) | Autonomous context layer |
| Vanna AI | No governance, requires manual training | Enterprise governance + RBAC |
| Seek AI | Proprietary, custom pricing | Open-standards, transparent pricing |
| ThoughtSpot | Months of setup, 6-figure cost | Hours of setup, usage-based pricing |

### 13.4 Pricing Comparison

| Product | Entry Level | Mid Market | Enterprise |
|---------|------------|------------|------------|
| Snowflake Cortex | Included (credit-based) | $2K-10K/mo (compute) | $10K-100K+/mo |
| Databricks Genie | Included (DBU-based) | $1K-5K/mo | $5K-50K+/mo |
| ThoughtSpot | N/A | N/A | $100K+/yr |
| Vanna AI (cloud) | Free | $50/user/mo | Custom |
| WrenAI (cloud) | Free | $99/user/mo | Custom |
| Seek AI | N/A | N/A | $50K+/yr |
| **Our Target** | **$0 (free tier)** | **$50/seat/mo** | **Custom** |

---

## 14. Research Gaps & Market Opportunities

### 14.1 Confirmed Market Gaps

| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Autonomous semantic layer** | No product auto-generates business context from schemas + docs | Our primary differentiator |
| **Cross-database NL2SQL with governance** | All warehouse-native solutions are locked to single platform | Addresses 68% of enterprises with multi-DB environments |
| **Self-improving accuracy** | Only Vanna has a learning loop, and it's manual | Automated learning from query corrections |
| **Mid-market NL2SQL (<$50K/yr)** | Most enterprise solutions start at $50K+/yr | Democratize data intelligence |
| **Schema intelligence for poor naming** | No product handles cryptic enterprise schemas well | "Works with your bad schema" is a feature |

### 14.2 Research Gaps to Validate

| Gap | Why It Matters | Validation Needed |
|-----|---------------|-------------------|
| Can autonomous schema discovery reach >80% accuracy without human input? | Core product hypothesis | Build prototype, test on 10 enterprise schemas |
| What is the optimal agent architecture for sub-2-second latency? | User experience requirement | Benchmark LangGraph vs custom pipeline |
| How many examples needed for self-learning loop to converge? | Product roadmap planning | Simulation with query log datasets |
| What is the ROCm vs CUDA cost difference at 10K QPD? | Infrastructure cost modeling | Run benchmark on MI300X vs H100 |
| Can a single model router achieve >95% routing accuracy? | Inference cost optimization | Build classifier, test on 10K queries |

---

## 15. Technology Trade-offs

### 15.1 Key Architectural Decisions

#### Decision 1: Monolithic vs Microservices

| Aspect | Monolithic | Microservices |
|--------|-----------|---------------|
| Development speed | Faster (MVP in weeks) | Slower (months) |
| Scalability | Vertical only | Horizontal |
| Deployment complexity | Low | High |
| Team scalability | Limited | High |
| Failure isolation | Poor | Good |
| **Recommendation** | **MVP** | **V1+** |

**Decision**: Start monolithic with clean module boundaries. Extract services as scaling demands.

#### Decision 2: Python vs Rust for Core Engine

| Aspect | Python | Rust |
|--------|--------|------|
| Development speed | Very fast | Slow |
| AI/ML ecosystem | Best in class | Limited |
| Performance | Moderate | Excellent |
| Memory safety | Managed | Guaranteed |
| Team availability | High | Low |
| **Recommendation** | **MVP** | **Core engine (Phase 2)** |

**Decision**: Python (FastAPI) for all application logic. Rust for the schema intelligence engine (following WrenAI's pattern with their Rust-based Wren Engine).

#### Decision 3: Graph Database vs Relational for Knowledge Layer

| Aspect | Graph (Neo4j) | Relational (Postgres) | Vector (Qdrant) |
|--------|--------------|----------------------|-----------------|
| Relationship traversal | Native, fast | Joins (slow at depth) | Not supported |
| Business term mapping | Natural fit | Workable | Limited |
| Operational complexity | Higher | Low (well-known) | Medium |
| Ecosystem maturity | Mature | Very mature | Maturing |
| **Recommendation** | **Phase 2** | **Phase 1** | **Phase 1** |

**Decision**: Start with Postgres (structured metadata) + Qdrant (vector embeddings). Add Neo4j knowledge graph in Phase 2 when relationship complexity demands it.

#### Decision 4: SQL Generation Approaches

| Approach | Accuracy | Latency | Cost | Maintainability |
|----------|----------|---------|------|-----------------|
| Zero-shot prompting | 50-60% | Low | Low | High |
| Few-shot + RAG | 65-80% | Medium | Medium | Medium |
| Multi-candidate + selection | 75-85% | High | High | Medium |
| Fine-tuned SQL model | 80-90% | Low | Medium (one-time) | Low (re-training) |
| Agentic pipeline (multi-step) | 80-90% | High | High | Low |
| Semantic layer + generation | 90-100% | Medium | Medium | Medium |

**Decision**: Tiered approach — RAG + multi-candidate for most queries, agentic pipeline for complex, fine-tuned model as we scale.

#### Decision 5: Embedding Model

| Model | Dimensions | Quality | Cost | ROCm |
|-------|-----------|---------|------|------|
| OpenAI text-embedding-3-small | 1536 | Excellent | API cost | N/A |
| OpenAI text-embedding-3-large | 3072 | Best | API cost | N/A |
| BGE-M3 (BAAI) | 1024 | Very Good | Free (self-host) | Yes |
| E5-mistral-7b-instruct | 4096 | Excellent | Medium | Yes |
| Nomic-embed-text-v1.5 | 768 | Good | Free | Yes |

**Decision**: BGE-M3 for self-hosted (no data leaves our infra), OpenAI for fallback. Dimension = 1024 (good balance of quality and storage cost).

---

## 16. Recommended Technology Stack

### 16.1 MVP Stack (Phase 1)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend Framework** | Python + FastAPI | Fast development, async support, best AI ecosystem |
| **Agent Orchestration** | LangGraph | Most mature DAG-based agent framework for NL2SQL |
| **Database Abstraction** | SQLAlchemy 2.0 + Alembic | Industry standard, supports 20+ dialects |
| **Vector Store** | Qdrant (self-hosted, K8s) | Best filtered search, Rust performance, ROCm compatible |
| **Structured Metadata** | PostgreSQL 16 | Well-known, pgvector ready for future, pg_audit for compliance |
| **Cache** | Redis | Session state, rate limiting, query result caching |
| **LLM Inference** | vLLM + SGLang (ROCm) | Both support AMD MI300X in production |
| **Primary Models** | Qwen2.5-72B + SQLCoder-7b | Open-source, ROCm support, strong SQL performance |
| **Cloud API Fallback** | OpenAI / Anthropic | For edge cases, burst capacity |
| **Auth** | Auth0 / Keycloak | OAuth2/OIDC, RBAC, SSO support |
| **Frontend** | React + Next.js | Rich ecosystem, SSR, TypeScript |
| **Infrastructure** | Kubernetes (EKS) | Cloud-agnostic, auto-scaling, self-healing |
| **IaC** | Terraform | Industry standard, multi-cloud |
| **CI/CD** | GitHub Actions | Tight integration, matrix testing |
| **Observability** | OpenTelemetry + Grafana + Loki + Tempo | Traces, metrics, logs unified |

### 16.2 Inference Stack (AMD Primary)

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Inference Engine** | vLLM (ROCm) | Production serving for open models |
| **Agent Inference** | SGLang (ROCm) | Structured output, tool use, agent loops |
| **Hardware** | 4-8x AMD MI300X (192GB each) | Initial production capacity |
| **Container Runtime** | ROCm + Docker + K8s with GPU operator |
| **Model Quantization** | FP8 / INT4 | MI300X supports FP8 natively |
| **Provider Abstraction** | Custom lightweight layer | Switch between AMD, NVIDIA, cloud APIs |

### 16.3 Development Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Primary language |
| Poetry | Dependency management |
| Ruff | Linting + formatting |
| mypy | Type checking |
| pytest + pytest-benchmark | Testing + performance regression |
| pre-commit | Git hooks for quality |
| Docker Compose | Local development |
| Kind / Minikube | Local Kubernetes testing |

---

## 17. Recommended Product Architecture

### 17.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                             │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │ Chat UI │  │ API/SDK  │  │ Slack   │  │ Embedded │  │ CLI    │ │
│  │ (React) │  │ (REST)   │  │ Bot     │  │ Widget   │  │        │ │
│  └─────────┘  └──────────┘  └─────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────┐
│                     API GATEWAY (Kong / Envoy)                      │
│          Auth, Rate Limiting, Routing, Audit Logging                │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────┐
│                       ORCHESTRATION LAYER                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  Classifier │  │   Planner    │  │  Executor   │  │ Validator│ │
│  │  Agent      │  │   Agent      │  │  Agent      │  │ Agent    │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  Schema     │  │  Business    │  │  Repair     │  │ Learning │ │
│  │  Retriever  │  │  Context     │  │  Agent      │  │ Agent    │ │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────┐
│                        KNOWLEDGE LAYER                              │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ Vector Store │  │  Metadata Store  │  │  Knowledge Graph     │  │
│  │ (Qdrant)     │  │  (PostgreSQL)    │  │  (Neo4j - Phase 2)  │  │
│  │ DDL embeds   │  │  Table/column    │  │  Business terms      │  │
│  │ Q&A pairs    │  │  relationships   │  │  Metric definitions  │  │
│  │ Documentation│  │  Query history   │  │  Org hierarchy       │  │
│  └──────────────┘  └──────────────────┘  └──────────────────────┘  │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────┐
│                       INFERENCE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐    │
│  │  vLLM + ROCm │  │SGLang + ROCm │  │   Cloud API Fallback   │    │
│  │  Open models │  │Agent-inference│  │  (OpenAI/Anthropic)    │    │
│  └──────────────┘  └──────────────┘  └────────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────┐
│                       DATABASE CONNECTORS                           │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐   │
│  │PG │ │My │ │SF │ │BQ │ │MS │ │Or │ │RS │ │CK │ │DB │ │...│   │
│  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 17.2 Data Flow (Query Request)

```
User: "What was our MRR by region last quarter?"

Step 1: Intent Classification
    → Classifier Agent: DATA_QUERY (confidence 0.97)
    → Off-topic check: PASS

Step 2: Schema Retrieval
    → Schema Retriever: Search Qdrant for "mrr", "region", "revenue"
    → Returns: 7 relevant tables (revenue_summary, customers, regions, ...)

Step 3: Business Context
    → Business Context Agent: Query metadata store
    → "MRR" → metric #42, defined as SUM(recurring_revenue) WHERE active=TRUE
    → "Last quarter" → temporal resolver: 2026-04-01 to 2026-06-30
    → "Region" → dimension: region_map table with hierarchy

Step 4: SQL Generation
    → Generator Agent (DeepSeek-V3): 
    → Produces 3 candidate queries (temperature 0.3, 0.5, 0.7)

Step 5: Validation
    → Syntax check: PASS (all 3)
    → Schema conformance: PASS (tables exist, columns valid)
    → Security scan: SELECT-only, no sensitive columns
    → Cost estimation: ~$0.02 compute
    → Best query selection: Candidate #2 (highest relevance score)

Step 6: Execution
    → Execute via read-only connection
    → Time: 340ms
    → Rows: 12

Step 7: Reflection
    → Reflector Agent: Results match expected pattern? YES
    → No repair needed

Step 8: Learning
    → Store query + SQL + result hash in Q&A pair store
    → Update query history index

Step 9: Response
    → Natural language: "MRR for Q2 2026 by region: NA $4.2M, EMEA $2.1M, APAC $1.8M..."
    → Visualization: bar chart (auto-selected)

Total latency target: < 3s (p95)
```

### 17.3 Module Breakdown

| Module | Responsibility | MVP | V1 |
|--------|---------------|-----|-----|
| **api-gateway** | Auth, routing, rate limiting, audit | Yes | Yes |
| **agent-orchestrator** | LangGraph pipeline, agent coordination | Yes | Yes |
| **schema-intelligence** | Schema introspection, embedding, indexing | Yes | Yes |
| **business-context** | Metric definitions, term resolution | Manual | Auto-discovery |
| **sql-generator** | LLM-based SQL generation | Yes (multi-candidate) | Yes (+ fine-tuned) |
| **validator** | Syntax, security, cost validation | Yes (basic) | Yes (full) |
| **executor** | Read-only query execution | Yes (single DB) | Yes (multi-DB) |
| **reflector** | Self-critique and repair | Simple | Advanced |
| **learner** | Feedback ingestion, model update | Manual | Automated |
| **visualizer** | Chart generation, NL summary | Basic | Advanced |
| **knowledge-store** | Qdrant + PostgreSQL | Yes | Yes (+ Neo4j) |
| **inference-proxy** | Model routing, provider abstraction | Yes | Yes |
| **dashboard-service** | Query history, usage analytics | No | Yes |
| **admin-console** | Schema management, RBAC config | Yes | Yes |

---

## 18. Technical Risks

### 18.1 Risk Register Summary

| ID | Risk | Impact | Probability | Mitigation |
|----|------|--------|-------------|------------|
| R-001 | Schema intelligence fails on cryptic enterprise schemas (>70% of tables unparseable) | Critical | Medium | Progressive enhancement: start with query-history-based discovery, add DDL parsing as fallback |
| R-002 | LLM hallucination produces confidently wrong SQL | Critical | High | Deterministic guardrails (syntax check, schema conformance, cost ceiling) + reflection agent | 
| R-003 | AMD ROCm compatibility gaps block model deployment | High | Medium | Hardware-agnostic inference abstraction; NVIDIA H100 as backup |
| R-004 | Multi-tenant data isolation breach | Critical | Low | Row-level security, tenant-scoped schema views, audit logging |
| R-005 | Cold start — no query history for self-learning loop | High | High | Bootstrap with DDL embeddings + synthetic Q&A generation |
| R-006 | Inference cost exceeds budget at scale | High | Medium | Tiered model routing (cheap for simple, expensive for complex) |
| R-007 | Enterprise sales cycle too long for runway | Critical | High | Self-serve onboarding, free tier, PLG motion alongside enterprise sales |
| R-008 | Single-database MVP limits market appeal | Medium | Medium | Launch with 5 most popular dialects (PG, MySQL, Snowflake, BigQuery, DuckDB) |
| R-009 | LLM API providers change pricing/terms unexpectedly | Medium | Low | Self-hosted open models as primary; cloud APIs as fallback |
| R-010 | Competition from Snowflake/Databricks AI features | Medium | Medium | Focus on cross-database + autonomous discovery — their moat is their weakness |

### 18.2 Key Mitigation Strategies

**R-001 (Schema Intelligence)**: Do not rely on DDL alone. Combine:
- Query history mining (most accurate for real usage patterns)
- Data profiling (detect data types, enum values, null ratios)
- LLM-based description generation (for columns with no documentation)
- Active learning prompts ("Does 'c1' represent customer count?")

**R-002 (Hallucination)**: The 7-layer guardrail stack is non-negotiable. Every generated query passes through:
1. SQL syntax validation
2. Schema conformance (tables/columns exist)
3. Security policy enforcement (read-only, RBAC-scoped)
4. Cost ceiling check
5. Result plausibility check (if historical data available)

**R-005 (Cold Start)**: Use a "schema bootstrapper" that:
1. Connects to the database
2. Introspects all tables and columns
3. Uses an LLM to generate descriptions from column names, data types, and sample values
4. Generates synthetic Q&A pairs for the 50 most common query patterns
5. Indexes everything in the vector store

---

## 19. Open Research Questions

### 19.1 Questions Requiring Validation

| # | Question | Hypothesized Answer | Validation Method |
|---|----------|-------------------|-------------------|
| 1 | Can autonomous semantic discovery reach >80% accuracy without human input? | Yes, for well-documented schemas. No, for legacy systems — but 60-70% is sufficient for effective NL2SQL | Build prototype, test on 10 enterprise schemas of varying quality |
| 2 | What is the optimal agent orchestration pattern for sub-2s latency? | Parallel agents for independent tasks (schema retrieval + business context), sequential for dependent (generate → validate) | Benchmark LangGraph with different parallelism strategies |
| 3 | How many Q&A pairs are needed for the self-learning loop to converge? | ~100 per domain for basic coverage, ~500 for 80%+ recall | Simulate with public query log datasets |
| 4 | What is the accuracy-cost tradeoff of fine-tuned vs prompted models for NL2SQL? | Fine-tuned 7B model can match prompted 70B model on specific domains | Train SQLCoder-7b on enterprise schemas, compare with GPT-4o |
| 5 | Can a router model achieve >95% accuracy in classifying query complexity? | Yes, with well-structured training data (1000+ examples per category) | Build classifier, evaluate on 10K diverse queries |
| 6 | What is the ROCm vs CUDA TCO at production scale (10K QPD)? | ROCm MI300X is 20-30% cheaper than H100 at equivalent throughput | Run standardized benchmark on both platforms |
| 7 | How much context compression is needed for 1000+ column schemas? | Need to reduce from ~50K tokens to <8K tokens without losing critical context | Evaluate different pruning strategies (popularity-based, embedding-similarity) |
| 8 | Can SQL dialect differences be handled by context alone, or is transpilation needed? | Context is sufficient for 90%+ of queries | Test with dialect documentation in prompt vs transpilation engine |

### 19.2 Questions with External Dependencies

| # | Question | Dependency | Monitoring |
|---|----------|------------|------------|
| 9 | Will AMD maintain ROCm software investment? | AMD corporate strategy | Track ROCm release cadence, community adoption |
| 10 | Will open-source LLMs close the gap with GPT-4o/Claude for NL2SQL? | Model development community | Track BIRD leaderboard, SQL-specific benchmarks |
| 11 | Will Snowflake/Databricks add cross-database support? | Competitive dynamics | Monitor product announcements |
| 12 | Will the MCP (Model Context Protocol) become a universal standard? | Anthropic + industry adoption | Track A2A/MCP adoption rates |

---

## 20. Final Recommendations

### 20.1 Build vs Buy Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Schema intelligence engine** | **Build** | Core differentiator; no existing solution |
| **NL2SQL agent pipeline** | **Build on LangGraph** | Framework is open-source; custom agent logic is our IP |
| **Business context layer** | **Build** | Autonomous discovery is our primary moat |
| **Vector store** | **Buy (Qdrant)** | Mature open-source; no value in building |
| **LLM inference** | **Build abstraction, use open-source** | vLLM/SGLang are mature; we need routing logic |
| **Auth/Access control** | **Buy (Auth0/Keycloak)** | Commodity; security expertise not our differentiator |
| **Frontend UI** | **Build (React)** | User experience is product differentiation |
| **Knowledge graph** | **Phase 2 (Neo4j)** | Not needed for MVP; critical for complex queries |
| **SQL execution** | **Build (SQLAlchemy-based)** | Thin layer over existing mature libraries |

### 20.2 Architecture Principles

1. **Hardware-agnostic inference**: Never depend on a single GPU architecture. Abstract provider behind an interface.
2. **Fail-closed security**: Every guardrail layer defaults to blocking. Safety over convenience.
3. **Self-improving by default**: Every query execution feeds the learning loop. The system gets better with use.
4. **No manual semantic modeling**: If a human has to write YAML, we've failed. Automate everything.
5. **Cross-database from day one**: Design connectors as plugins. MVP launches with 5 dialects.
6. **Deterministic guardrails over probabilistic generation**: Use LLMs for what they're good at (generation) and deterministic code for what it's good at (validation).
7. **Observability at every layer**: Every agent decision, every query, every validation result is logged and traceable.

### 20.3 The Autonomous Context Layer — Our Core Differentiator

This is the single most important architectural decision:

**What it does**: Automatically builds a business knowledge layer by:
1. Connecting to the database and introspecting all schemas
2. Mining query history for real relationship patterns
3. Ingesting documentation (if available) for term definitions
4. Using LLMs to generate descriptions for undocumented columns
5. Cross-referencing business terms across tables to discover metrics
6. Presenting the discovered context for human validation
7. Continuously improving based on query feedback

**What competitors do instead**:
- Snowflake: You write YAML
- Databricks: You curate Unity Catalog
- WrenAI: You author MDL files
- Vanna: You manually provide training data

**Why it's defensible**: The quality of the context layer improves with:
- More schemas scanned (network effects)
- More query history analyzed (data network effects)
- More human feedback collected (learning effects)
- More documentation ingested (content moat)

Each of these creates switching costs. A competitor would need to replicate years of context accumulation.

### 20.4 Call to Action

Phase 0 research confirms: **There is a clear market opportunity for an autonomous, cross-database, enterprise NL2SQL platform with a self-improving context layer.**

The technology is ready:
- Multi-agent architectures are proven in production
- Open-source LLMs are at parity with commercial for SQL generation
- AMD ROCm provides a viable (and cost-advantaged) inference path
- Vector databases, RAG, and GraphRAG have matured

The gap is real:
- No product delivers autonomous semantic discovery
- Mid-market ($0-50K/yr) is underserved
- Multi-database enterprises have no unified solution

**Recommendation**: Proceed to Phase 1 (Product & Business) to define the vision, mission, ICP, and roadmap — then Phase 2 for detailed technical architecture.

---

## References

See [Research-Bibliography.md](./Research-Bibliography.md) for the complete reference list.
