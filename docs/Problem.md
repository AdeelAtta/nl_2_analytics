# Problem Statement

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Vision.md](./Vision.md), [Market-Analysis.md](./Market-Analysis.md), [Competitor-Analysis.md](./Competitor-Analysis.md), [Technical-Landscape-Report.md](./Technical-Landscape-Report.md) |

---

## 1. Executive Summary

Enterprise data is the most valuable asset most companies own. Yet the majority of employees cannot access it, the majority of data goes unanalyzed, and the tools that promise to solve this fail in production.

This is not a technology problem. The models are capable. The infrastructure exists. The problem is **architectural**: no existing solution connects the three critical layers — schema understanding, business knowledge, and governed execution — into a single reliable system.

The result: a $12.9M annual loss per enterprise from poor data quality and accessibility, 40-60% of analyst time wasted on routine queries, and a fundamental bottleneck on data-driven decision-making.

---

## 2. The Problem

### 2.1 Who Has the Problem

Every enterprise with more than one database and more than one analyst experiences this problem:

| Role | Pain Point | Frequency |
|------|-----------|-----------|
| **Product Manager** | Needs weekly user engagement data. Opens Jira ticket. Waits 2-5 days. | 3-5x/week |
| **Data Analyst** | 60% of time spent writing `SELECT ... FROM ... WHERE ... GROUP BY ...` for the 10th time this week. | Daily |
| **Head of Data** | Hired 5 analysts. Still can't keep up with demand. 80% of requests are "simple queries." | Quarterly planning |
| **CTO** | Has 12 databases across 3 clouds. No single person understands all of them. | Monthly review |
| **Business Stakeholder** | Given access to a BI tool but can't find the right dashboard. Needs a question answered that the dashboard wasn't built for. | Weekly |

### 2.2 The Data

| Metric | Value | Source |
|--------|-------|--------|
| Enterprise NL2SQL accuracy in production | **10-21%** | Spider 2.0 (ICLR 2025) |
| Academic benchmark accuracy | **85-92%** | Spider 1.0 |
| Enterprise data that goes unanalyzed | **68%** | IBM |
| Analyst time on routine SQL | **40-60%** | Multiple surveys |
| Annual loss per enterprise from poor data quality | **$12.9M** | Gartner |
| Applications per enterprise (average) | **897** | MuleSoft 2025 |
| CIOs who regret at least one AI vendor decision | **74%** | Dataiku/Harris Poll 2026 |

### 2.3 The Gap

```
100% │                                              ┌── Semantic Layer
     │                                              │  (Manual, weeks)
  80% │                    ┌────────────────────────┘
     │                    │ Academic Benchmarks
  60% │                    │ (Spider 1.0, BIRD)
     │                    │
  40% │                    │
     │                    │
  20% │                    │                    ┌── Enterprise Production
     │                    │                    │  (Spider 2.0, Real World)
   0% └────────────────────┴────────────────────┘
     2020        2022        2024        2026
```

**The gap is not getting smaller.** While benchmark scores rise, the complexity of enterprise environments also grows. Schema sizes increase. Data sources multiply. Business terminology evolves.

---

## 3. Root Causes

### 3.1 The Four Root Causes

Research identifies four recurring failure modes (Oracle OCI NL2SQL team, 2026):

#### Root Cause 1: Ambiguous Intent

> "How did OCI do last month?"

| Ambiguity | Possible Meaning |
|-----------|-----------------|
| "OCI" | Organization? Campaign? Region? Division? |
| "Do" | Revenue? Margin? Bookings? Growth? Customer count? |
| "Last month" | Calendar month? Fiscal period? Trailing 30 days? Data-refresh cutoff? |
| "How" | Total value? Trend? Comparison to target? Comparison to prior period? |

**Why existing solutions fail**: They assume intent is clear. They do not resolve ambiguity against business context.

#### Root Cause 2: Missing Business Knowledge

Enterprise terms have meanings that are never in the schema:

- "Healthy growth accounts" → defined by a policy document, not a column name
- "North Europe" → a specific set of countries that changes quarterly
- "MOC 3" → Monthly Operating Cycle 3, an internal fiscal period
- "Net revenue" → may be computed differently for sales vs finance vs product

**Why existing solutions fail**: They rely on column names that don't capture business meaning.

#### Root Cause 3: Physical Schema Complexity

Enterprise schemas are optimized for storage, not retrieval:

- 100-10,000+ tables with cryptic names
- Multiple versions of the same logical table
- Denormalized structures requiring multi-step joins
- Embedded data (XML, JSON, arrays) requiring unnesting
- Missing or implicit foreign key relationships

**Why existing solutions fail**: They cannot handle schema complexity at scale. Performance degrades linearly with table count.

#### Root Cause 4: Context Sensitivity

The same question has different answers depending on:

- Who is asking (role, team, geography)
- When they ask (current date, fiscal period, data freshness)
- Where the data lives (Snowflake vs Postgres vs both)
- What they've asked before (conversation history)

**Why existing solutions fail**: They treat every question as an independent, context-free transaction.

### 3.2 The Existing "Solutions" (That Don't Work)

#### Approach 1: Warehouse-Native AI

- Snowflake Cortex Analyst
- Databricks AI/BI Genie
- Google BigQuery Gemini
- Microsoft Copilot for Fabric

**Why they fail**: Single-platform only. Require manual YAML/semantic modeling. Cannot cross database boundaries. Limited to simple queries. (Source: Product documentation, ColRows comparison Jun 2026)

#### Approach 2: Open-Source NL2SQL Frameworks

- Vanna AI
- WrenAI
- DB-GPT

**Why they fail**: Require engineering teams to operate. No enterprise governance. Inconsistent accuracy. No self-learning loop (except Vanna, which requires manual training curation). (Source: Sudipta Pathak benchmark Feb 2026)

#### Approach 3: Enterprise BI with AI Features

- ThoughtSpot Spotter
- Looker + Gemini
- Hex

**Why they fail**: Months of setup. 6-figure annual costs. Fixed to specific data models. AI is a feature, not the core architecture. (Source: Product documentation, Basedash comparison 2026)

#### Approach 4: Fine-Tuned SQL Models

- SQLCoder
- Defog
- BIRD-Talon

**Why they fail**: Models are just one component. They cannot resolve ambiguity, access business knowledge, or enforce governance. A correct model is necessary but insufficient. (Source: dbt Labs benchmark 2026)

---

## 4. Why This Is Difficult

### 4.1 Technical Challenges

| Challenge | Why Hard | Impact |
|-----------|----------|--------|
| Schema understanding at scale | 1000+ columns, cryptic names, no documentation | 10-21% accuracy |
| Business knowledge capture | Tacit, distributed across people, docs, and code | System doesn't know what it doesn't know |
| Cross-database semantics | Same term = different meaning in different databases | Incorrect join paths |
| Cold start | Zero query history for new connections | Cannot use learning loop initially |
| Multi-tenancy | Enterprise + team + user-level context | RBAC complexity |
| Latency vs accuracy | Complex analysis takes time; users expect instant answers | Suboptimal trade-offs |
| Model selection | No single model excels at all query types | Overpay for simple queries or fail on complex ones |

### 4.2 Business Challenges

| Challenge | Why Hard | Impact |
|-----------|----------|--------|
| Enterprise sales cycle | 6-18 months for procurement | Burn rate management |
| Data privacy regulations | GDPR, HIPAA, SOC 2, CCPA across jurisdictions | Architecture complexity |
| Customer diversity | Each enterprise has unique schemas, terminology, policies | Hard to productize |
| Price sensitivity | Mid-market (<$50K/yr) is underserved but price-conscious | Unit economics |
| Competitive pressure | Snowflake/Databricks are adding AI features monthly | Need to move fast |

---

## 5. Consequences of Not Solving This

| Timescale | Consequence | Affected |
|-----------|-------------|----------|
| **Daily** | Decisions made without data, or made slowly | All business stakeholders |
| **Weekly** | Analyst team bottlenecks, ticket queues grow | Data team, requesters |
| **Monthly** | Data quality issues go undetected, wrong numbers used | Executives |
| **Quarterly** | Missed market opportunities from slow analysis | Company |
| **Annually** | $12.9M+ lost per enterprise, competitive disadvantage | Shareholders |

---

## 6. Validation

### 6.1 Evidence the Problem Is Real

| Source | Finding |
|--------|---------|
| Spider 2.0 (ICLR 2025) | Best enterprise NL2SQL accuracy: 17.1%. The problem is unsolved. |
| Oracle OCI NL2SQL team (2026) | Four root causes identified by a team with enterprise AI expertise. |
| dbt Labs (Apr 2026) | Even with best models, raw text-to-SQL achieves only 45-60% on complex schemas. |
| Cisco NL2SQL case study (Feb 2025) | Production deployment required months of schema curation. |
| LinkedIn SQL Bot (Engineering blog) | Millions of tables; brute-force schema retrieval is impossible. |

### 6.2 Evidence the Market Will Pay to Solve It

| Source | Finding |
|--------|---------|
| Gartner (2026) | Agentic AI market: $7.55B (2025) → $199B (2034) |
| ThoughtSpot pricing | Enterprise customers pay $100K+/year for natural language querying |
| Snowflake/Databricks AI features | Both sold as premium capabilities within $B+ platforms |
| Seek AI pricing | $50K+/year for governed NL2SQL alone (no visualization, no dashboards) |

---

## 7. What Solving This Unlocks

| Unlocked Capability | Impact |
|---------------------|--------|
| **Self-serve analytics for all employees** | Remove the SQL gatekeeper. 5x increase in data-informed decisions. |
| **10x analyst productivity** | 60% of routine SQL eliminated → 60% more high-value analysis. |
| **Unified data understanding** | One platform that knows all schemas, all terms, all relationships. |
| **Proactive intelligence** | Not just question-answering, but insight delivery without being asked. |
| **Data literacy at scale** | Every employee learns from the platform's explanations and context. |

---

## 8. References

| Source | Relevance |
|--------|-----------|
| [Technical-Landscape-Report.md](../Technical-Landscape-Report.md) §3 | Detailed enterprise pain point analysis |
| [Market-Analysis.md](./Market-Analysis.md) | Market sizing and opportunity |
| [Competitor-Analysis.md](./Competitor-Analysis.md) | Why existing solutions fail |
| Spider 2.0 (ICLR 2025), arXiv:2411.07763 | Enterprise NL2SQL accuracy benchmark |
| Oracle OCI NL2SQL blog (2026) | Four root causes of enterprise failure |
| dbt Labs Semantic Layer Benchmark (2026) | Raw text-to-SQL accuracy ceiling |
| Dataiku/Harris Poll (2026) | CIO regret rate on AI vendor decisions |
| IBM data silos statistic | 68% of enterprise data unanalyzed |
| Gartner data quality cost | $12.9M average annual loss per enterprise |
