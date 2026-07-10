# Phase 1 Executive Review

**Enterprise Data Intelligence Platform**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Ready for Phase 2 |
| **Version** | 1.0 |
| **Phase 1 Documents** | 12 docs across 4 categories (Foundation, Market, Strategy, Execution) |

---

## 1. Executive Summary

We are building an **autonomous enterprise data intelligence platform** — a system that understands every database, every business term, and every analytical pattern in an organization, then makes that intelligence accessible through natural language, governed SQL, and self-learning improvement.

**Core thesis**: The NL2SQL market gap is not model accuracy (models are good enough) — it is **setup friction**. Every existing product requires manual YAML, MDL, or semantic modeling. Our autonomous context layer eliminates this entirely, turning a 2-6 week setup into 15 minutes.

**Why now**: Multi-agent architectures are proven (Gartner: 1,445% surge), open-source LLMs have reached parity with commercial models (SQLCoder-7b-2 beats GPT-4 on ratio queries), AMD ROCm is production-grade for inference, and 74% of CIOs regret at least one AI vendor decision — creating a window for a new entrant.

**Financial thesis**: $28B TAM by 2030 (Data Intelligence + NL2SQL). Target: $450K ARR Year 1 → $17.5M Year 3 → $137.5M Year 5. Breakeven in Q3 Year 3. Pre-seed $500K-$1M, Seed $3M-$5M, Series A $10M-$15M.

---

## 2. Product Vision

| Dimension | Definition |
|-----------|-----------|
| **North Star** | Every enterprise question receives a trusted, governed answer within seconds — without requiring a human to write SQL, model a semantic layer, or understand the underlying schema. |
| **Long-term goal** | AI operating system for enterprise data: knows, answers, discovers, learns, acts, integrates. |
| **Not building** | A BI tool, ETL pipeline, vector database, fine-tuned model company, general-purpose AI chatbot, or Snowflake/Databricks replacement. |
| **Capability evolution** | NL2SQL (Year 1) → Multi-DB Intelligence (Year 2) → Proactive Insights (Year 3) → Autonomous Data Workflows (Year 4-5). |
| **Core philosophy** | Intelligence, not automation. Trust through governance. Autonomous by default. Cross-platform by design. Self-improving system. |

**Year 1 targets**:
- >85% execution accuracy on known queries
- 5 database dialects: PostgreSQL, MySQL, Snowflake, BigQuery, DuckDB
- Enterprise governance: RBAC, audit, column-level security, anomaly detection
- Self-learning loop improving with each query
- Slack, Teams, and API integration

---

## 3. Mission Statement

> **Make every enterprise data asset accessible and understandable to every stakeholder through autonomous AI — without requiring technical expertise, manual curation, or data movement.**

### Core Tenets

| Tenet | Evidence |
|-------|----------|
| **Zero Configuration Intelligence** | dbt Labs 2026: even minimal modeling improves accuracy 20-30%. We automate that modeling. |
| **Trust Through Transparency** | ASK-TARA: 90K queries, zero security incidents. Deterministic policy enforcement + transparency = trust. |
| **Continuous Learning** | Vanna AI's self-learning loop: highest open-source approach at 40% execution accuracy. |
| **Cross-Platform by Design** | 68% of enterprise data goes unanalyzed due to silos (IBM). Single-platform solutions address <50% of data. |
| **Enterprise-Grade Governance** | Fail-closed architecture prevents the most dangerous failure: confidently wrong answers. |

### Non-Negotiables

Accuracy over speed. Flexibility over automation. Security over convenience. Simplicity over power. Autonomy within governance.

---

## 4. Ideal Customer Profile (ICP)

### Primary ICP: Mid-Market (50-5,000 employees)

| Attribute | Value |
|-----------|-------|
| **Company size** | 50-5,000 employees |
| **Data team** | 2-20 data analysts/engineers |
| **Database count** | 3-20 across 2+ platforms |
| **Annual data tool spend** | $10K-$200K |
| **Current frustration** | Analyst team is bottleneck; 2-5 day query turnaround |
| **Buying authority** | Head of Data (champion) → CTO (technical decision) → CFO (budget approval) |

### Primary Personas

| Persona | Pain | Buying Criteria |
|---------|------|-----------------|
| **Head of Data** | 40-60% analyst time on routine SQL; can't scale | Accuracy (30%), setup ease (20%), security (15%), cross-DB (15%) |
| **Analytics Engineer** | 60% work is boilerplate queries; constant interruptions | SQL correctness, trust, learning from corrections |
| **CTO / VP Eng** | Slow decisions; data team bottleneck; no audit visibility | Security, governance, scalability, ROI |

### Secondary Personas

| Persona | Pain | Usage Pattern |
|---------|------|---------------|
| **Product Manager** | 2-5 day wait for data; can't iterate | Asks 3-10 queries/week; trusts system; never looks at SQL |
| **Business Analyst** | Limited to pre-built dashboards; manual data pulls | Heavy user once empowered; cross-source queries |
| **C-Suite Executive** | Different answers from different teams | 1-5 strategic questions/week; needs trust above all |

### Buying Center Dynamics

Head of Data = Champion. CTO/VP Eng = Technical decision. Security = Veto power. CFO = Budget. Free tier → champion inside. Pilot on non-critical DB → prove accuracy. Expand to production.

---

## 5. Top 10 Customer Pain Points

| # | Pain Point | Root Cause | Current Workaround | Severity |
|---|-----------|------------|-------------------|----------|
| 1 | Analysts spend 40-60% of time on routine SQL queries | No self-serve data access layer | Hire more analysts (doesn't scale) | Critical |
| 2 | Business stakeholders wait 2-5 days for simple data questions | SQL bottleneck | Jira ticket queue, shadow Excel | Critical |
| 3 | No single person understands all 10+ databases | Tribal knowledge undocumented | Onboarding takes 2-4 weeks per hire | High |
| 4 | Multiple databases with inconsistent schemas/terminology | No unified business glossary | Manual mapping, error-prone | High |
| 5 | Existing NL2SQL products require weeks of YAML/semantic modeling | Product architecture flaw | Hire consultants or abandon adoption | High |
| 6 | Business users limited to pre-built dashboards; can't explore ad hoc | BI tools require data team for new queries | Manual report generation | High |
| 7 | Same metric reported differently across departments | No single source of truth | Endless alignment meetings | Medium |
| 8 | Data quality issues go undetected until quarterly reviews | No proactive anomaly detection | Manual data audits | Medium |
| 9 | Compliance/audit requirements not met by current tools | No query audit trail in NL2SQL tools | Don't use NL2SQL for governed data | Medium |
| 10 | 74% of CIOs chose wrong AI vendor in last 18 months | Feature claims exceed production reality | Procurement paralysis | Medium |

---

## 6. Market Size

### Market Stack

| Layer | Market Size | Growth |
|-------|-------------|--------|
| Data & Analytics Platforms | $340B (IDC 2026) | 15% YoY |
| **AI-Powered Data Intelligence (TAM)** | **$28B by 2030** | **>50% YoY** |
| Natural Language to SQL (subset) | $500M-$1B in 2026 | >50% YoY |
| **Serviceable Market (SAM)** | **$312M** (Year 5 target) | — |
| **Serviceable Obtainable (SOM)** | **$17.5M-$52.5M** (Year 3) | — |

### TAM Breakdown

| Segment | Organizations | Annual Spend | TAM |
|---------|--------------|-------------|-----|
| Large Enterprise (>5,000) | 3,000 | $200K-$2M | $1.5B-$3B |
| Mid-Market (500-5,000) | 45,000 | $25K-$200K | $3B-$5B |
| SMB (50-500) | 300,000 | $5K-$50K | $5B-$10B |

### Key Market Trends Driving Us

| Trend | Evidence | Implication |
|-------|----------|-------------|
| Multi-agent architectures standard | Gartner: 1,445% surge in inquiries | Architecture validated |
| Open-source LLMs at parity with commercial | SQLCoder-7b-2 > GPT-4 on ratio queries | Self-hosted inference viable |
| AMD ROCm production-grade | vLLM/SGLang support mature | 20-30% cost advantage |
| Mid-market underserved | All solutions start at $50K+/year | Pricing advantage |
| Warehouse-native AI = single-platform | Snowflake/Databricks locked to own stack | Cross-platform differentiation |

---

## 7. Competitor Comparison

### Competitive Tier Overview

| Tier | Competitors | Strength | Weakness | Our Advantage |
|------|------------|----------|----------|---------------|
| **1: Warehouse-Native AI** | Snowflake Cortex, Databricks Genie, BigQuery Gemini, MS Copilot for Fabric | Zero data movement, native governance | Single-platform, manual YAML | Cross-DB, autonomous setup |
| **2: Enterprise BI + AI** | ThoughtSpot, Looker+Gemini, Hex | Mature BI, visualization | Months setup, 6-figure cost, fixed models | Hours setup, 10-50x cheaper |
| **3: Open-Source NL2SQL** | Vanna AI, WrenAI, DB-GPT | Flexible, self-hostable | Requires engineering team, limited governance | Complete product, not library |
| **4: Pure-Play NL2SQL** | Seek AI, Dataherald, Text2SQL | Focused accuracy | Narrow scope, no platform | Platform breadth, self-learning |

### Feature Matrix (Key Differentiators)

| Feature | Us | Snowflake | Databricks | Vanna | WrenAI | Seek AI | ThoughtSpot |
|---------|----|-----------|------------|-------|--------|---------|-------------|
| Autonomous context discovery | ✅ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Cross-database | ✅ | ✗ | ✗ | ✅lib | ✅eng | ✗ | ✗ |
| Self-learning loop | ✅ | ✗ | Limited | ✅manual | ✗ | ✗ | ✗ |
| No manual modeling | ✅ | ✗ | ✗ | ✗train | ✗MDL | ✗ | ✗months |
| RBAC + column security | ✅ | ✅native | ✅Unity | ✗ | ✅limited | ✅ | ✅ |
| Mid-market pricing (<$50K) | ✅ | ✗ | ✗ | ✅$50/s | ✅$99/s | ✗ | ✗ |

### Our Market Position

Only product in the **multi-database + high governance** quadrant. WrenAI is closest but requires manual MDL (AGPL licensed). No competitor offers autonomous context discovery.

---

## 8. Our Primary Differentiators

### Three-Pillar Moat

| Pillar | Description | Competitor Status | Defensibility |
|--------|-------------|-------------------|---------------|
| **1. Autonomous Context Layer** | AI discovers business meaning from DDL, query history, docs, and BI metadata — zero YAML | No competitor does this. All require manual modeling or training. | 12-18 month head start. Competitors' business models depend on setup friction (Snowflake = consumption, ThoughtSpot = services, WrenAI = MDL). |
| **2. Cross-Platform Semantic Bridge** | Unified understanding across Snowflake, Postgres, BigQuery, MySQL — same term resolves correctly per database | Warehouse-native = single-platform by design. OSS = requires connector code per platform. | 18-24 month to compete. Retrofitting cross-DB support into warehouse-native architecture is fundamentally difficult. |
| **3. Self-Learning Intelligence** | Every query + correction + feedback improves accuracy. Compounding data network effect. | Vanna: manual training. WrenAI: no learning. Enterprise: no learning. | Compounding moat over time. A 2027 entrant needs 18+ months of accumulated query history. |

### Secondary Differentiators

- **AMD-first inference**: 20-30% cost advantage over NVIDIA
- **10-layer fail-closed policy enforcement stack**: Production-proven (ASK-TARA: 90K queries, 0 incidents); L2-L10 fully deterministic
- **Multi-candidate SQL generation**: 3 candidates, auto-select best
- **Reflection + repair loop**: Self-critique and iterative improvement
- **Explainability by default**: Every answer shows SQL, reasoning, confidence
- **Slack/Teams native**: Query from where you work

---

## 9. Why Customers Will Choose Us

| Customer Role | Why They Choose Us vs Competitors |
|--------------|----------------------------------|
| **Head of Data** | "Setup in 15 minutes vs 2-6 weeks. My analysts stop writing boilerplate SQL. I can prove ROI within a week." |
| **Analytics Engineer** | "Finally, a tool that understands our messy schemas without me hand-holding it. And it learns from my corrections." |
| **CTO** | "One intelligence layer across all our databases. No vendor lock-in. Full audit trail. SOC 2 compliant." |
| **Product Manager** | "I get data answers in seconds instead of waiting days. I can iterate on my questions." |
| **Business Analyst** | "I can finally ask questions beyond what my dashboard shows me. In plain English." |
| **CFO** | "$50/seat/month vs $100K/yr for ThoughtSpot. The ROI calculation takes 30 seconds." |

### Key Buying Criteria Ranking (from Head of Data persona research)

1. **Accuracy on our specific schemas** (30%) — Must work on real, messy enterprise data
2. **Ease of setup** (20%) — No manual modeling is the primary differentiator
3. **Security and RBAC** (15%) — Enterprise table stakes; failure here = no deal
4. **Cross-database support** (15%) — Multi-DB environments are the norm, not exception
5. **Price / ROI justification** (10%) — Must be clearly cheaper than hiring analysts
6. **Integration with existing stack** (10%) — Slack, Teams, dbt, BI tools matter for retention

---

## 10. Business Model & Pricing Summary

### Revenue Model

Hybrid usage-based + seat-based SaaS. 70% subscription, 20% self-hosted licenses, 10% professional services by Year 3.

### Pricing Tiers

| Tier | Price | Seats (min) | Queries/seat/mo | Databases | Target |
|------|-------|-------------|-----------------|-----------|--------|
| Free | $0 | 3 | 33 | 1 (PG, DuckDB) | Evaluation |
| Starter | $50/seat/mo (~$23% off annual) | 5 | 200 | Up to 3 | Small teams |
| Pro | $150/seat/mo (~$23% off annual) | 10 | 1,000 | Up to 10 | Mid-market |
| Enterprise | Custom from $25K/yr | Unlimited | Custom | Unlimited | Large enterprise |

### Unit Economics

| Metric | Value |
|--------|-------|
| Weighted avg cost per query | ~$0.006 (self-hosted primary) |
| Revenue per query (Starter) | $0.25 |
| Gross margin (per query) | ~97.6% |
| Gross margin (Year 1) | 70-83% |
| Gross margin (Year 3 target) | 85-90%+ |
| LTV:CAC (mid-market target) | >5:1 |
| Monthly churn (mid-market) | 3-5% |
| Annual churn (enterprise) | 5-10% |

### Revenue Projections (Base Scenario)

| Year | Customers | Avg ACV | ARR | Burn | Headcount |
|------|-----------|---------|-----|------|-----------|
| 1 (MVP) | 25 | $18K | $450K | $1.13M | 6-8 |
| 2 | 150 | $25K | $3.75M | $3.2M | 20 |
| 3 | 500 | $35K | $17.5M | $6.84M | 40 |
| 4 | 1,200 | $45K | $54M | $12M | 70 |
| 5 | 2,500 | $55K | $137.5M | $20M | 120 |

**Breakeven**: Q3 Year 3 (Net income positive: +$8.4M)

### Funding Requirements

| Round | Amount | Timeline | Use |
|-------|--------|----------|-----|
| Pre-seed | $500K-$1M | Now | 4-6mo runway, prototype |
| Seed | $3M-$5M | Q1 2027 | 12-18mo, MVP launch, first 20 customers |
| Series A | $10M-$15M | Q4 2027-Q1 2028 | 18mo growth, 200+ customers |
| Series B | $25M-$40M | 2029 | Market expansion, verticals |

---

## 11. Product Roadmap

### Now (Q3-Q4 2026) — MVP

| Quarter | Milestone |
|---------|-----------|
| Q3 2026 | First prototype: single-DB, PostgreSQL, simple queries |
| Q3 2026 | Autonomous context layer V1 — DDL + basic schema inference |
| Q3 2026 | 10-layer policy enforcement framework operational |
| Q4 2026 | Multi-DB: PostgreSQL, MySQL, DuckDB, Snowflake, BigQuery |
| Q4 2026 | Tiered model routing: SQLCoder-7b / Qwen2.5-72B / DeepSeek-V3 |
| Q4 2026 | Free tier launch (3 users, 100 queries/mo) |

### Next (Q1-Q4 2027) — Growth

| Quarter | Milestone |
|---------|-----------|
| Q1 2027 | SaaS platform launch (Starter + Pro) |
| Q1 2027 | RBAC + column-level security |
| Q1 2027 | Self-learning loop V1 |
| Q2 2027 | Slack/Teams integration |
| Q2 2027 | SQL Server + Oracle connectors |
| Q3 2027 | Enterprise VPC deployment |
| Q3 2027 | SSO/SAML/SCIM |
| Q3 2027 | BI integration (Tableau, Looker, Metabase) |
| Q4 2027 | Dashboard builder |
| Q4 2027 | Learned model routing |
| Q4 2027 | SOC 2 Type II certification |

### Later (2028-2030)

| Phase | Theme | Key Capabilities |
|-------|-------|-----------------|
| Phase 3 (2028) | Intelligence Everywhere | Cross-DB joins, Embedded API, Marketplace, NL dashboards, Data quality monitoring |
| Phase 4 (2029) | Proactive Intelligence | Proactive alerts, Root cause analysis, NL reporting, On-prem K8s, Industry verticals |
| Phase 5 (2030) | Autonomous BI | Self-driving analytics, NL ETL, Predictive analytics, Air-gapped, BI tool replacement |

---

## 12. Success Metrics

### By Category

| Category | Key Metrics (Year 1 → Year 3) |
|----------|-------------------------------|
| **Business** | ARR $450K → $17.5M. NRR >110% → >120%. Gross margin >70% → >85%. LTV:CAC >5:1 → >10:1. CAC <$2K → <$1K. |
| **Product** | WAU >60%. Queries/user/week >15. Time to first query <5min. D30 retention >80%. Monthly churn <5%. NPS >40. |
| **Engineering** | Uptime 99.9%. API P50 <500ms, P95 <3s. Error rate <1%. MTTR <15min. Deploy frequency weekly → daily. |
| **AI** | SQL accuracy >85%. Business accuracy >80%. First-query success >70%. Context precision@10 >0.90. Guardrail FP rate <1%, FN rate <0.1%. |

### Self-Learning Loop Metrics

| Metric | Target |
|--------|--------|
| Feedback collection rate | >10% of queries |
| Learning-to-production latency | <24 hours |
| Accuracy improvement (monthly) | >2% |
| Cold start duration | <30 days to >70% first-query success |

### Phase Transition Gates

| From | To | Required |
|------|----|----------|
| MVP | Beta | 9/9 MVP goals met |
| Beta | V1 | 25 paying customers, NPS > 30, accuracy > 75% |
| V1 | Enterprise | 200 customers, NRR > 110%, accuracy > 85% |
| Enterprise | Platform | $17.5M ARR, gross margin > 85%, cross-DB joins functional |
| Platform | Vision | $54M ARR, proactive insights live |

---

## 13. Top 10 Strategic Risks

| # | Risk | Impact | Probability | Mitigation |
|---|------|--------|-------------|------------|
| 1 | Autonomous context layer achieves <50% accuracy on legacy schemas | USP claim undermined; no product | Medium | Set expectations: "70%+ autonomous with human validation workflow." Bootstrap with synthetic data. |
| 2 | Enterprise sales cycle depletes runway before revenue materializes | Company runs out of money | High | Product-led growth generates cash while enterprise builds. Self-serve mid-market is primary motion. |
| 3 | Competitor ships auto-discovery first (WrenAI, Vanna, Snowflake) | Loss of primary differentiator | Medium | 12-18 month head start. File patents. Document priority date. Move fast. |
| 4 | Inference costs don't decrease as expected | Margin compression | Medium | Self-hosted primary inference + tiered routing. Cloud API as fallback only. |
| 5 | Self-learning loop requires more data than expected | Accuracy doesn't compound | Medium | Bootstrap with synthetic Q&A + public SQL datasets. Manual curation as backup. |
| 6 | Cross-DB semantic resolution too complex for MVP | Feature delay vs promise | Medium | Launch single-DB, roadmap multi-DB clearly. Don't promise cross-DB joins in Year 1. |
| 7 | Open-source alternative achieves parity | Loss of differentiation | Medium (12-18mo) | Maintain UX + governance + data network effect advantages. |
| 8 | Snowflake/Databricks add cross-DB support | Loss of primary wedge | Low (18-24mo) | Build deeper schema intelligence moat before they catch up. |
| 9 | AMD ROCm roadmap slips | Hardware availability delays | Medium | Maintain CUDA path in inference abstraction layer. Cloud APIs as temporary fallback. |
| 10 | AI winter / funding contraction | Can't raise next round | Low | Capital-efficient growth (15-person team Year 1). Clear ROI metrics for investors. |

---

## 14. Top 10 Assumptions

| # | Assumption | Confidence | Validation Required Before | Validation Method |
|---|-----------|------------|---------------------------|-------------------|
| 1 | Autonomous context discovery can achieve >70% accuracy without human input | Low-Medium | Phase 2 architecture freeze | Build prototype against 5 enterprise schemas; measure precision/recall |
| 2 | Mid-market (50-500 emp) will pay $50-150/seat/month for NL2SQL | Medium | Beta launch (Q1 2027) | Free tier → pricing page → conversion data |
| 3 | Self-hosted LLMs (SQLCoder, Qwen, DeepSeek) reach sufficient accuracy for production | Medium | Alpha (Q3 2026) | Benchmark against our schemas across all 3 tiers |
| 4 | Tiered routing model can correctly classify query complexity >85% of the time | Medium | Alpha (Q3 2026) | Test classifier against labeled query corpus |
| 5 | 5 database dialects (PG/MySQL/Snowflake/BQ/DuckDB) cover 80%+ of enterprise market | High | MVP (Q4 2026) | Cross-reference with MuleSoft connectivity data |
| 6 | 10-layer policy enforcement achieves <0.1% false negative rate on dangerous queries | Medium-High | Alpha (Q3 2026) | Red-team testing against 1,000+ attack scenarios |
| 7 | Cold start self-learning can be bootstrapped with synthetic data | Low-Medium | Phase 2 (Q1 2027) | Measure accuracy improvement trajectory from synthetic seed |
| 8 | 20%+ gross margin improvement from AMD ROCm vs NVIDIA | Medium | Infrastructure phase (Q3 2026) | A/B test identical workloads on ROCm vs CUDA |
| 9 | Enterprise VPC/on-prem customers will accept same pricing as cloud | Medium | Enterprise beta (Q3 2027) | Customer interviews during sales process |
| 10 | D30 retention > 80% is achievable with autonomous setup value prop | Medium | Beta (Q1 2027) | Measure retention cohorts from free tier |

---

## 15. Top 10 Open Questions

| ID | Question | Impact | Research Required | Priority |
|----|----------|--------|------------------|----------|
| Q-001 | Can autonomous context discovery achieve >70% precision on enterprise schemas with cryptic naming? | Core USP viability | Test on 5+ real enterprise schemas | P0 |
| Q-002 | What is the optimal cold-start strategy for the self-learning loop? | Learning loop viability | Compare: synthetic data, public SQL corpuses, hybrid | P0 |
| Q-003 | What is the actual accuracy of tiered model routing on real enterprise queries? | Cost structure | Build classifier, test on mixed query workload | P0 |
| Q-004 | What is the optimal embedding strategy for enterprise schema elements? | Context retrieval quality | Compare BGE-M3, voyage-2, fine-tuned BGE | P0 |
| Q-005 | Can a single multi-agent pipeline handle all query types (simple to complex)? | Architecture viability | Implement prototype, test across query difficulty spectrum | P0 |
| Q-006 | What is the real-world false negative rate of the 10-layer policy enforcement stack? | Trust/safety | Red-team with 1,000+ scenarios | P0 |
| Q-007 | How much training data is needed for each new database dialect? | Connector roadmap | Build connector for MySQL, measure accuracy vs PG | P1 |
| Q-008 | What is acceptable query latency for business users? | UX standards | User research during free tier | P1 |
| Q-009 | What percentage of enterprise users will correct/approve queries (feedback rate)? | Learning loop efficacy | Measure during free tier | P1 |
| Q-010 | What schema size (tables/columns) causes context retrieval to degrade? | Scale limits | Stress-test context layer with 10K+ table schemas | P1 |

**All open questions tracked in full detail at**: [Open-Questions.md](./Open-Questions.md) (30 questions, 7 external dependencies, 6 deferred decisions)

---

## 16. Decisions That Will Directly Impact Phase 2 Architecture

| # | Decision | Architecture Impact | Source Document |
|---|----------|-------------------|-----------------|
| 1 | **Autonomous context layer is the core differentiator** | Must be designed as a modular, extensible pipeline (not monolith). Must support DDL, query history, docs, and BI metadata sources. | Vision.md, USP.md |
| 2 | **Multi-database from day one** | Pluggable connector architecture through SQLAlchemy. Dialect-specific SQL generation. Cross-platform semantic resolution. | Roadmap.md, Technical-Landscape-Report.md |
| 3 | **Self-learning loop is fundamental to product value** | Feedback collection must be built into every query path from the start. Vector store for Q&A pairs. Training pipeline architecture. | USP.md, Mission.md |
| 4 | **10-layer fail-closed policy enforcement stack** | Policy enforcement is not optional — it is the architecture. Every query must pass all 10 layers (L1: LLM-assisted intent, L2-L10: fully deterministic) before execution. | Vision.md, Technical-Landscape-Report.md |
| 5 | **Tiered model routing (cheap → expensive)** | Router must be fast (sub-100ms classification). Inference abstraction layer must support hot-swappable model backends. | Technology-Recommendations.md |
| 6 | **Self-hosted inference primary, cloud fallback** | Inference abstraction layer must be hardware-agnostic (AMD ROCm + CUDA + cloud APIs). No vendor-specific code in business logic. | Technology-Recommendations.md |
| 7 | **API-first + Slack/Teams native** | Architecture must support multiple frontends from a single backend API. Chat integrations are first-class citizens, not afterthoughts. | Vision.md |
| 8 | **Multi-tenant cloud SaaS primary deployment** | Tenant isolation model. K8s-native architecture. Stateless services. Terraform IaC. | Technical-Landscape-Report.md |
| 9 | **Mid-market PLG go-to-market** | Self-serve onboarding, free tier → paid conversion. No sales calls required for Starter tier signup. | Business-Model.md |
| 10 | **Phase 0 tech stack decisions are locked** | LangGraph (agent orchestration), Qdrant (vector store), vLLM + SGLang (inference), FastAPI (backend), React/Next.js (frontend). | Technology-Recommendations.md |

---

## 17. Features Intentionally Deferred to Later Releases

| Feature | Deferred To | Rationale |
|---------|-------------|-----------|
| Dashboard builder / visualization | Phase 2 (Q4 2027) | MVP returns SQL + data table. Viz is value-add, not core. |
| Fine-tuned LLM models | Phase 3 (2028) | Prompt engineering + RAG sufficient for MVP. Fine-tuning adds complexity without proportional gain. |
| Cross-database joins (single question across DBs) | Phase 3 (2028) | Requires mature context layer + semantic bridge. Core NL2SQL must work first. |
| Learned model routing | Phase 2 (Q4 2027) | Manual routing rules sufficient for MVP. Need production data to train router. |
| Proactive insights / anomaly detection | Phase 3-4 (2028-2029) | Requires query history accumulation + baseline models. |
| On-premises K8s deployment | Phase 4 (2029) | Operational complexity too high for early stage. Cloud-first. |
| Air-gapped deployment | Phase 5 (2030) | Niche requirement; focus on cloud + VPC for first 3 years. |
| Embedded API / white-label | Phase 3 (2028) | Requires mature, stable API surface. Focus on direct product first. |
| Marketplace (third-party connectors) | Phase 3 (2028) | Ecosystem play; premature when core product isn't proven. |
| Mobile apps | Not planned | Web-first + Slack/Teams native covers mobile use cases. |
| BI tool replacement | Not until Phase 5 (2030) | We integrate with BI tools; we don't replace them until much later. |
| ETL / data pipeline creation | Phase 5 (2030) | We consume from data stores; we don't build pipelines. |

---

## 18. MVP Definition

### In Scope (MVP — Q3-Q4 2026)

| Category | In Scope |
|----------|----------|
| **Databases** | PostgreSQL first (single-DB), then MySQL, DuckDB, Snowflake, BigQuery |
| **Query types** | Simple SELECT queries with filters, GROUP BY, basic JOINs |
| **Context layer** | DDL parsing + basic column name inference. No query history mining yet. |
| **Model routing** | Manual rules-based tiered routing (SQLCoder-7b / Qwen2.5-72B) |
| **Security** | 10-layer policy enforcement stack operational. Read-only queries only. |
| **Self-learning** | Feedback capture + storage. No active model improvement from feedback yet. |
| **Frontend** | Web chat interface. SQL output + data table. |
| **Integration** | API (REST). No Slack/Teams yet. |
| **Deployment** | Single-tenant cloud SaaS. No VPC/on-prem. |
| **Pricing** | Free tier only. No billing system. |
| **Auth** | Email + password. No SSO/SAML. |

### Out of Scope (MVP)

| Category | Out of Scope |
|----------|-------------|
| **Not supported** | Complex multi-join queries, subqueries, CTEs, window functions, DDL/DML |
| **Not supported** | Oracle, SQL Server, Redshift, ClickHouse, Databricks, SQLite |
| **Not supported** | Visualization, dashboards, charts |
| **Not supported** | Slack/Teams integration |
| **Not supported** | RBAC / column-level security |
| **Not supported** | SSO / SAML / SCIM |
| **Not supported** | Audit log UI (logged internally only) |
| **Not supported** | Learned model routing |
| **Not supported** | Self-learning loop active improvement |
| **Not supported** | BI tool integration |
| **Not supported** | On-premises / VPC deployment |
| **Not supported** | Enterprise pricing / billing |

### MVP Exit Criteria

| # | Criteria | Measurement |
|---|----------|-------------|
| 1 | 10 benchmark queries produce correct SQL against PostgreSQL | Execution-pass test |
| 2 | Context auto-discovers 100-table schema in <5 minutes | Timing test |
| 3 | 100% pass on policy enforcement test suite (100 injection scenarios) | Red-team test |
| 4 | Same NL query works across all 5 database dialects | Cross-DB test |
| 5 | Tiered routing selects correct model >85% of the time | Classifier accuracy test |
| 6 | Feedback capture rate >5% of queries | Product telemetry |
| 7 | Full audit trail, searchable within 5 seconds | Performance test |
| 8 | 100 free tier signups in first month post-launch | Product analytics |
| 9 | Inference abstraction layer runs on AMD ROCm + cloud fallback | Integration test |

---

## 19. Go-to-Market Summary

### Strategy: Product-Led Growth (PLG) → Sales-Led Enterprise

| Phase | Motion | Target | Channels |
|-------|--------|--------|---------|
| MVP (2026) | Founder-led | 20-50 free tier signups | Technical content, conference talks, OSS contribution |
| Beta (Q1-Q2 2027) | Self-serve PLG | 25 paying customers | Product-led: free → trial → paid |
| V1 (Q3-Q4 2027) | PLG + Early Sales | 150 customers | Self-serve + 1-2 SDRs |
| Enterprise (2028) | Sales-led + PLG | 500 customers (50 enterprise) | Field sales (5 reps) + marketing |
| Scale (2029+) | Sales + Ecosystem | 1,200+ customers | Enterprise sales, channel partners, marketplace |

### Pricing Strategy

- **Free tier**: Generous enough to demonstrate value, capped to prevent abuse. PostgreSQL + DuckDB only.
- **Starter** ($50/seat): Self-serve PLG. No sales calls required. Annual contract gives ~23% discount.
- **Pro** ($150/seat): Self-serve + optional sales. Higher governance + larger query allowances.
- **Enterprise** (from $25K/yr): Sales-led. Custom deployment, SSO, dedicated support.

### Key Go-to-Market Assumptions

| Assumption | Confidence | Risk |
|------------|-----------|------|
| Free → paid conversion > 3% | Medium | Industry average 2-5% for B2B SaaS |
| Mid-market self-serve works without sales | Medium | Need to test pricing page conversion |
| Enterprise sales cycle 3-6 months | Medium | Could be 6-18 months for regulated industries |
| Content marketing generates qualified leads | High | Well-established channel for developer tools |

---

## 20. Final Recommendations

### Strategic

1. **Lead with autonomous context layer as primary differentiator** — No competitor claims this. It is the reason customers choose us. Every piece of marketing, every demo, every conversation should start here.

2. **Build in public** — Open-source non-core components (connectors, visualizer library). Publish architecture blog posts. Give conference talks. This builds credibility, attracts talent, and creates community.

3. **Move fast on the 12-18 month head start** — The window is real but finite. Ship MVP in Q4 2026. Get first 25 paying customers by Q2 2027. The competitive response clock is ticking.

4. **Mid-market PLG is the primary motion** — Don't build an enterprise sales team before product-market fit. Self-serve generates revenue AND product feedback faster than enterprise sales cycles.

### Product

5. **Depth over breadth in Year 1** — Nail Postgres first. Nail 100-table schema understanding. Make 20 simple queries work perfectly before expanding to 50 medium queries.

6. **Bootstrap the self-learning loop aggressively** — Generate synthetic Q&A pairs from real schemas. Seed with public SQL benchmarks. The cold start is the biggest risk to the learning moat.

7. **Test the policy enforcement stack mercilessly** — A single false negative (dangerous query allowed) in MVP could kill enterprise trust permanently. Red-team before every release.

### Technical (Inputs to Phase 2)

8. **Design the context layer as an extensible pipeline** — Sources may increase (DDL → query history → docs → BI metadata). Make adding sources a configuration change, not an architecture change.

9. **Build the inference abstraction layer first** — GPU vendor lock-in is a strategic risk. The abstraction layer must support AMD ROCm + CUDA + cloud APIs from day one, even if only one path is implemented initially.

10. **Architect for multi-tenancy from day one** — The SaaS platform must support tenant isolation, tenant-specific context, and tenant-specific learning. Retrofitting multi-tenancy is expensive and risky.

---

## Appendix A: Unresolved Decisions

| # | Decision | Options | Deadline | Owner |
|---|----------|---------|----------|-------|
| D-01 | Authentication provider: Auth0 vs Clerk vs Keycloak | Auth0 (mature, SOC 2), Clerk (modern DX), Keycloak (self-hosted) | Phase 2 start | CTO |
| D-02 | Visualization library: Chart.js vs D3 vs Apache ECharts vs Recharts | Lightweight (Chart.js), flexible (D3), feature-rich (ECharts), React-native (Recharts) | Phase 2 start | Frontend lead |
| D-03 | LLM fine-tuning framework: Axolotl vs Unsloth vs TRL | Ecosystem maturity vs performance vs simplicity | Phase 3 start | ML Lead |
| D-04 | Feedback collection UX: Thumbs up/down vs rating vs correction input | Simpler (thumbs) vs richer (correction) | Phase 2 UX design | Product |
| D-05 | Monetization for free tier: ads vs limited features vs time-limited vs usage-capped | Currently: usage-capped (100 queries/mo) | Before scale | CEO |
| D-06 | SLA tiers: are they tied to support tiers or product tiers? | Currently: Starter 99.5%, Pro 99.9%, Enterprise 99.95% | Before public launch | CTO |

---

## Appendix B: Assumptions Requiring Customer Validation

| # | Assumption | Validation Plan | Timeline | Success Criteria |
|---|-----------|----------------|----------|-----------------|
| A-01 | Mid-market will pay $50-150/seat/month | Price page A/B test during free tier | Q1-Q2 2027 | >3% conversion at stated prices |
| A-02 | Autonomous setup (no YAML) is the #1 buying criteria | Customer interviews during beta | Q1 2027 | >50% cite this as primary reason |
| A-03 | Business users accept 70% accuracy if system is transparent | User research during free tier | Q4 2026-Q1 2027 | NPS > 30 with 70% accuracy |
| A-04 | Analysts want to see/edit SQL always | UX instrumentation | Q4 2026 | >80% of analysts view SQL >50% of time |
| A-05 | 5 database dialects cover 80%+ of enterprise market | Survey beta customers | Q1-Q2 2027 | >80% use one of the 5 supported |
| A-06 | Slack/Teams is the primary integration need | Beta feature request tracking | Q2 2027 | >60% of requests mention chat integration |
| A-07 | Enterprise VPC deployment is a gating requirement for >$50K deals | Enterprise sales discovery | Q3 2027 | >50% of $50K+ deals require VPC |
| A-08 | Annual contracts are acceptable for mid-market | Pricing page data | Q1-Q2 2027 | >40% choose annual over monthly |
| A-09 | Self-learning loop measurably improves accuracy within 30 days | Cohort analysis | Q1-Q2 2027 | >5% accuracy improvement MoM |
| A-10 | Customers will invest time in correcting/approving queries | Product telemetry | Q4 2026-Q1 2027 | >10% feedback rate after 30-day ramp |

---

## Appendix C: Recommendations That Changed After Research

| # | Recommendation | Changed From | Changed To | Rationale |
|---|---------------|-------------|------------|-----------|
| C-01 | **Tiered model routing** | Single model for all queries | SQLCoder-7b (simple) / Qwen2.5-72B (medium) / DeepSeek-V3 (complex) / GPT-4o (fallback) | 50-70% cost reduction without sacrificing complex query accuracy. Router accuracy is the key risk. |
| C-02 | **Self-hosted primary inference** | Cloud API primary | Self-hosted open models primary, cloud fallback only | Open-source LLMs reached parity (SQLCoder-7b-2 > GPT-4 on ratio queries). 20-30% cost advantage. ROCm maturity confirmed. |
| C-03 | **Cross-DB joins deferred** | Single-DB → multi-DB → cross-DB joins | Cross-DB joins moved from Year 2 to Year 3-4 | Complexity of semantic resolution across databases is significantly higher than single-DB NL2SQL. Not required for MVP value prop. |
| C-04 | **Mid-market PLG primary** | Enterprise sales-led as primary | Mid-market PLG primary, enterprise secondary | Enterprise sales cycle (6-18 months) too long for runway. PLG generates revenue faster and provides product feedback loop. |
| C-05 | **Multi-candidate SQL generation** | Single best SQL output | 3 candidates, auto-select best, show alternatives | Research shows multi-candidate + selection improves accuracy 10-15% over single generation. Worth the additional inference cost. |
| C-06 | **10-layer policy enforcement (not 3)** | 3 layers: auth, validation, audit | 10 layers: Intent Classification (LLM) → SQL Sanitization → RBAC Scoping → Cost Ceiling → SQL Validation → Read-Only Exec → Audit Logging → Data Classification → Advanced Validation → Anomaly Detection | ASK-TARA production system proves comprehensive deterministic policy enforcement achieves zero incidents. Partial enforcement is dangerous. |
| C-07 | **No fine-tuning in MVP** | Fine-tune SQLCoder for enterprise schemas | Prompt engineering + RAG only for MVP | Fine-tuning adds months of complexity. RAG + prompt engineering achieves sufficient accuracy for MVP with faster iteration. Fine-tuning planned for Phase 3. |

**End of Phase 1 Executive Review**
