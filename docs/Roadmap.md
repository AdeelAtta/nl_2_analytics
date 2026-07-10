# Roadmap

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Goals.md](./Goals.md), [Business-Model.md](./Business-Model.md), [Vision.md](./Vision.md) |

---

## 1. Roadmap Philosophy

We follow a **build-measure-learn** approach with three time horizons:

| Horizon | Timeframe | Focus | Risk Level |
|---------|-----------|-------|------------|
| **Now** | 0-6 months | Core NL2SQL functional, prove value | Build risk |
| **Next** | 6-18 months | Scale, enterprise features, platform | Product-market fit risk |
| **Later** | 18-60 months | Ecosystem, embedded AI, autonomous BI | Market expansion risk |

---

## 2. Now (Q3 2026 - Q4 2026) — MVP

### Theme: "Make SQL Obvious"

**Goal**: Working NL2SQL that beats existing solutions on ease of setup.

| Quarter | Milestone | Dependencies | Success Metric |
|---------|-----------|-------------|----------------|
| **Q3 2026** | First prototype: single-database, PostgreSQL only, simple queries | GPU hardware acquired, dev environment | 10 test queries work end-to-end |
| **Q3 2026** | Autonomous context layer V1 — DDL parsing + basic schema inference | Database connectors | Schema auto-discovery for 100 tables < 5 min |
| **Q3 2026** | 10-layer policy enforcement framework operational | Context layer | 0 security incidents |
| **Q4 2026** | Multi-DB MVP (PostgreSQL, MySQL, DuckDB, Snowflake, BigQuery) | Q3 work | 5 dialects functional |
| **Q4 2026** | Tiered model routing (SQLCoder-7b / Qwen2.5-72B / DeepSeek-V3) | Inference abstraction layer | 3 models operational, routing > 85% accuracy |
| **Q4 2026** | Free tier launch (3 users, 100 queries/mo) | MVP complete | 100 signups |

### Now — Key Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| PostgreSQL first (single-DB) | Most common OSS DB, simple connector | ✅ Confirmed |
| Skip LLM fine-tuning initially | Prompt engineering + RAG sufficient for MVP | ✅ Confirmed |
| Manual tiered routing (not learned) | Reduce complexity; learned routing Phase 2 | ✅ Confirmed |
| No UI visualization yet | Output SQL + execute, return table; viz Phase 2 | ✅ Confirmed |
| Professional services manual | No self-service setup; early customers get hands-on | ✅ Confirmed |

---

## 3. Next (Q1 2027 - Q4 2027) — Growth

### Theme: "Trust at Scale"

**Goal**: Enterprise-ready platform with governance, collaboration, and proven ROI.

| Quarter | Milestone | Dependencies | Success Metric |
|---------|-----------|-------------|----------------|
| **Q1 2027** | SaaS platform launch (Starter + Pro tiers) | API, billing, onboarding flow | 25 paying customers |
| **Q1 2027** | RBAC + column-level security | Auth system (Auth0 / Clerk) | SOC 2 control pass |
| **Q1 2027** | Self-learning loop V1 | Feedback collection from users | 10% query feedback rate |
| **Q2 2027** | Slack / Teams integration | API | 40% daily active on Slack |
| **Q2 2027** | Query history UI + audit log | Database + storage | Searchable, exportable |
| **Q2 2027** | SQL Server + Oracle connectors | Driver licenses + testing | Connector parity |
| **Q3 2027** | Enterprise dedicated deployment (VPC) | Terraform modules, networking | First enterprise deployment |
| **Q3 2027** | SSO / SAML / SCIM | Identity integration | Enterprise requirement met |
| **Q3 2027** | Context layer V2 — BI integration (Tableau, Looker, Metabase) | BI API research | Query history from BI tools |
| **Q4 2027** | Dashboard builder (basic charts from SQL results) | Visualization library | Basic viz functional |
| **Q4 2027** | Learned model routing | Production query data | Routing accuracy > 90% |
| **Q4 2027** | SOC 2 Type II certification | Security program | Certification achieved |

### Next — Key Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| Auth0/Clerk for auth | Mature SSO, SOC 2 compliant | 🔍 Research ongoing |
| Chart.js + custom renderer for viz | Lightweight, no heavy BI tool dependency | 💡 Recommendation |
| Weekly deploy cadence | Balance velocity vs stability | 💡 Recommendation |
| Enterprise VPC first (not on-prem) | Less operational complexity | ✅ Confirmed in Phase 0 |

---

## 4. Later (2028-2030) — Scale & Ecosystem

### Phase 3 (2028): "Intelligence Everywhere"

| Component | Description |
|-----------|-------------|
| **Codex-level context** | Schema intelligence reaches > 95% accuracy |
| **Embedded API** | Embeddable NL2SQL widget for any SaaS application |
| **Cross-database joins** | Query across PostgreSQL + Snowflake + BigQuery in single question |
| **Marketplace** | Third-party semantic models, connectors, visualization packs |
| **Natural language dashboards** | "Show me revenue by month for the last year" → dashboard |
| **AI agent credits** | Per-call billing model for embedded use cases |
| **Data quality monitoring** | Anomaly detection as additional module |

### Phase 4 (2029): "Proactive Intelligence"

| Component | Description |
|-------------|-------------|
| **Proactive alerts** | "Your revenue dropped 15% yesterday — run the query?" |
| **Root cause analysis** | "Why did revenue drop?" → multi-table drill-down |
| **Natural language reporting** | Scheduled reports via natural language |
| **On-prem K8s deployment** | Customer-managed Kubernetes cluster |
| **Industry verticals** | Healthcare (HIPAA), Finance (SOX), Retail |
| **Multi-model queries** | Combine SQL + vector + graph in single query |

### Phase 5 (2030): "Autonomous BI"

| Component | Description |
|-------------|-------------|
| **Self-driving analytics** | AI proactively finds insights without prompts |
| **Air-gapped deployment** | No internet access required |
| **Custom model fine-tuning** | Customer-specific SQL generation models |
| **Natural language ETL** | "Create a pipeline that joins orders and returns" |
| **Predictive analytics** | "What will our revenue be next quarter?" |
| **BI tool replacement** | Full analytics platform replaces traditional BI |

---

## 5. Deployment Timeline

| Phase | Deployment Mode | Timeframe | Customer Verticals |
|-------|----------------|-----------|-------------------|
| Now | Cloud SaaS (single-tenant isolation) | 2026 | Tech startups, mid-market |
| Next | Cloud SaaS + dedicated VPC | 2027 | Regulated enterprises |
| Phase 3 | SaaS + VPC + on-prem | 2028 | Financial services |
| Phase 4 | On-prem K8s + VPC + SaaS | 2029 | Healthcare, government |
| Phase 5 | Air-gapped + all deployment modes | 2030 | Defense, intelligence |

---

## 6. AI Model Roadmap

| Phase | Self-Hosted Inference | Cloud Fallback | Embeddings |
|-------|----------------------|----------------|------------|
| Now | SQLCoder-7b-2, Qwen2.5-72B | GPT-4o-mini | BGE-M3 |
| Next | + DeepSeek-V3 (self-hosted) | GPT-4o, Claude Sonnet | BGE-M3 (fine-tuned) |
| Phase 3 | + Fine-tuned routing model | Claude Opus | Domain-adapted BGE |
| Phase 4 | + Customer fine-tunes | As needed | Custom embedding model |
| Phase 5 | + Next-gen open models | Edge case only | Learned embeddings |

---

## 7. Engineering Team Growth

| Phase | Team Size | Key Hires |
|-------|-----------|-----------|
| Now | 3-4 | Founding CTO, 2 ML engineers, 1 full-stack |
| Next | 10-15 | Backend, ML, DevOps, frontend, QA |
| Phase 3 | 20-30 | Platform, security, solutions engineering |
| Phase 4 | 30-50 | Enterprise support, industry vertical teams |
| Phase 5 | 50-80 | Research, product, ecosystem partners |

---

## 8. Key Assumptions & Risks

| Assumption | Confidence | Risk if Wrong | Mitigation |
|------------|-----------|---------------|------------|
| Self-hosted LLMs reach sufficient accuracy | Medium | Must rely on expensive cloud APIs | Invest early in prompt engineering; cloud API as backup |
| Enterprises willing to migrate from ThoughtSpot/Databricks | Medium | Long sales cycles | Start with mid-market; land-and-expand |
| Context layer accuracy exceeds 85% within 6 months | Low-Medium | Poor accuracy = no product | Bootstrap with synthetic data; iterate fast |
| AMD ROCm roadmap stays on schedule | Medium | Hardware availability delays | Maintain CUDA path as fallback in inference abstraction layer |
| SOC 2 achievable within 12 months | High | Delays enterprise sales | Start SOC 2 readiness in Phase 0 |
| Hybrid cloud inference costs stay <$0.01/query | Medium | Margin compression | Tiered routing + aggressive caching |

---

## 9. References

| Source | Relevance |
|--------|-----------|
| [Goals.md](./Goals.md) | Specific milestones with acceptance criteria |
| [Vision.md](./Vision.md) | Long-term product direction |
| [Business-Model.md](./Business-Model.md) | Revenue and growth milestones by phase |
| [Technology-Recommendations.md](./Technology-Recommendations.md) | Technology choices by phase |
