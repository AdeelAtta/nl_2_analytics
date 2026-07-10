# Feature Prioritization Matrix

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Classification** | Must Have (MVP) / Should Have (V1) / Could Have (V2+) / Won't Have (for now) |

---

## Priority Definitions

| Classification | Meaning | Timeline | Customer Impact if Missing |
|---------------|---------|----------|---------------------------|
| **P0 — Must Have (MVP)** | Ship-blocking. Product is non-functional without this. | Q3-Q4 2026 | Product doesn't work |
| **P1 — Should Have (V1)** | Customer-blocking for paid adoption. Table stakes for enterprise. | Q1-Q4 2027 | Won't buy, but might try free |
| **P2 — Could Have (V2+)** | Competitive differentiator or expansion feature. | 2028+ | Would like it, not a blocker |
| **P3 — Won't Have (for now)** | Intentional deferral. Aligns with later phases. | 2029+ | Not expected |

---

## 1. Core NL2SQL Pipeline

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Single-DB NL2SQL (PostgreSQL) — basic SELECT, WHERE, GROUP BY, JOIN | **Must Have (MVP)** | Core product. Without this, nothing works. | Goals MVP-01, Roadmap Q3 2026 |
| Multi-candidate SQL generation (3 candidates, auto-select best) | **Must Have (MVP)** | 10-15% accuracy improvement over single generation. Low complexity. | USP §4, Competitor Analysis §6 |
| Reflection + repair loop (self-critique and iterative improvement) | **Must Have (MVP)** | Critical accuracy booster. Rerun failed queries with error feedback. | USP §4, Competitor Analysis §6 |
| Tiered model routing (SQLCoder-7b / Qwen2.5-72B / DeepSeek-V3 / GPT-4o fallback) | **Must Have (MVP)** | 50-70% cost reduction vs single expensive model. | Goals MVP-05, Technology-Recommendations |
| Explainability by default (show SQL, reasoning, confidence, alternatives) | **Must Have (MVP)** | Trust requirement. ASK-TARA proven approach. | USP §4, Mission §2 |
| SQL output + data table display | **Must Have (MVP)** | Minimum viable output. No visualization required. | Vision Year 1, Roadmap "No viz in MVP" |
| User can see and edit generated SQL before execution | **Must Have (MVP)** | Analyst trust requirement. Customer-Personas §9 insight. | Customer-Personas §9 |
| Basic web chat interface | **Must Have (MVP)** | Primary user interaction surface. | Roadmap Q3-Q4 2026 |
| REST API | **Must Have (MVP)** | API-first architecture. Enables all integrations. | Vision §4.1, Competitor Analysis §6 |
| Complex query support (CTEs, subqueries, window functions, multi-join) | **Should Have (V1)** | MVP starts with simple queries. Complex support needed for real adoption. | Roadmap Q1-Q4 2027 |
| Learned model routing (from production data) | **Should Have (V1)** | Requires production query data to train. Manual rules sufficient for MVP. | Goals V1-04, Roadmap Q4 2027 |
| Natural language dashboard generation | **Should Have (V1)** | "Show me revenue by month" → chart. High value for business users. | Goals V1-03, Vision Year 2 |
| Cross-database joins (single question across PG + Snowflake + BQ) | **Could Have (V2+)** | Requires mature context layer + semantic bridge. High complexity. | Goals ENT-02, Roadmap Phase 3 |
| Multi-model queries (SQL + vector + graph) | **Could Have (V2+)** | Niche requirement. Expand query surface area. | Goals PLAT-05, Roadmap Phase 4 |

---

## 2. Context Layer

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| DDL parsing + schema introspection | **Must Have (MVP)** | Foundation of context layer. Extract table/column names, types, constraints. | Goals MVP-02, USP §3.1 |
| Basic column name inference ("c1" → "customer_id") | **Must Have (MVP)** | Minimum viable business meaning extraction. | USP §3.1, Vision Year 1 |
| 100-table schema auto-discovery in <5 minutes | **Must Have (MVP)** | MVP exit criteria. | Goals MVP-02, Success-Metrics §4 |
| Query history mining for join patterns + popular columns | **Should Have (V1)** | Requires production query data to mine. Starts empty at cold start. | USP §3.1, Roadmap Q1-Q2 2027 |
| Business description generation for tables/columns | **Should Have (V1)** | LLM-powered description generation. Improves discoverability. | USP §3.1 |
| Application documentation ingestion (RAG) | **Should Have (V1)** | Extract business terms and metric formulas from existing docs. | USP §3.1 |
| BI tool metadata integration (Tableau, Looker, Metabase) | **Should Have (V1)** | Mine dashboard definitions and metric references. | Goals V1-02, Roadmap Q3 2027 |
| dbt model import | **Should Have (V1)** | Leverage existing semantic work. High value for dbt users. | Vision Year 2, USP §5.1 |
| Knowledge graph linking business terms to physical schemas | **Could Have (V2+)** | Cross-database semantic resolution. Phase 2-3 complexity. | Vision Year 2, Roadmap Phase 3 |
| Cross-platform semantic resolution (same term, different DBs) | **Could Have (V2+)** | Core of cross-DB value prop. Requires mature context layer. | USP §3.2, Vision Year 2 |
| Context discovery rate >95% schema elements | **Could Have (V2+)** | Stretch target for context layer maturity. | Success-Metrics §5.1 |

---

## 3. Security & Governance

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| 10-layer policy enforcement stack (Intent Classification → SQL Sanitization → RBAC → Cost Ceiling → SQL Validation → Read-Only → Audit Logging → Data Classification → Advanced Validation → Anomaly Detection) | **Must Have (MVP)** | Non-negotiable. Fail-closed architecture. L2-L10 fully deterministic. Single false negative = trust broken. | Goals MVP-03, USP §4, Technology-Recommendations |
| Input sanitization (SQL injection prevention) | **Must Have (MVP)** | Part of policy enforcement stack (L2). 100% injection prevention target. | Goals MVP-03 |
| Query cost ceiling (prevent runaway queries) | **Must Have (MVP)** | Part of policy enforcement stack (L4). Prevents accidental expensive queries. | Technology-Recommendations |
| Read-only query enforcement | **Must Have (MVP)** | Part of policy enforcement stack (L6). No DDL/DML can execute. | Technology-Recommendations |
| Basic audit logging (internal — query + result + user + timestamp) | **Must Have (MVP)** | Part of policy enforcement stack (L7). Stored for later use. No UI needed in MVP. | Goals MVP-08 |
| Intent classification (detect non-query requests) | **Must Have (MVP)** | Part of policy enforcement stack (L1). First layer of defense. LLM-assisted. | Technology-Recommendations |
| RBAC — role-based access control | **Should Have (V1)** | Enterprise table stakes. Required for SOC 2 + customer security review. | Goals BETA-02, Roadmap Q1 2027 |
| Column-level security | **Should Have (V1)** | Restrict sensitive columns (PII, financial) per role. | Goals BETA-02, Roadmap Q1 2027 |
| SSO / SAML / SCIM | **Should Have (V1)** | Enterprise gating requirement. Cannot sell enterprise without it. | Goals BETA-04, Roadmap Q3 2027 |
| Audit log UI (searchable, exportable, filterable) | **Should Have (V1)** | Enterprise compliance requirement. MVP just stores internally. | Roadmap Q2 2027 |
| Audit log SIEM integration (Splunk, Datadog) | **Should Have (V1)** | Enterprise security team requirement. | Goals V1-05 |
| SOC 2 Type II certification | **Should Have (V1)** | Trust signal for enterprise. Takes 6-12 months to achieve. Start early. | Goals BETA-08, Roadmap Q4 2027 |
| 99.9% uptime SLA (Pro tier) | **Should Have (V1)** | Paid tier requirement. | Goals V1-06 |
| 99.95% uptime SLA (Enterprise tier) | **Could Have (V2+)** | Enterprise requirement for critical workloads. | Pricing §2.4 |
| Data encryption at rest + in transit | **Should Have (V1)** | Compliance requirement. Must be designed into architecture. | Success-Metrics §6 |
| Immutable, encrypted audit for regulated industries | **Could Have (V2+)** | Financial services / healthcare requirement. | Pricing §2.4 |

---

## 4. Database Connectors

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| PostgreSQL connector | **Must Have (MVP)** | First DB supported. Most common open-source database. | Roadmap Q3 2026 |
| MySQL connector | **Must Have (MVP)** | Part of 5-dialect MVP. Second most common OSS DB. | Goals MVP-04, Roadmap Q4 2026 |
| DuckDB connector | **Must Have (MVP)** | Part of 5-dialect MVP. Embedded analytics, fast growing. | Goals MVP-04 |
| Snowflake connector | **Must Have (MVP)** | Part of 5-dialect MVP. Most popular cloud warehouse in ICP. | Goals MVP-04 |
| BigQuery connector | **Must Have (MVP)** | Part of 5-dialect MVP. Google Cloud ecosystem. | Goals MVP-04 |
| Pluggable connector architecture (SQLAlchemy) | **Must Have (MVP)** | Architectural decision. Single interface for all DB dialects. | Technology-Recommendations, USP §3.2 |
| SQL Server connector | **Should Have (V1)** | Enterprise requirement. Very common in ICP. | Goals BETA-06, Roadmap Q2 2027 |
| Oracle connector | **Should Have (V1)** | Enterprise requirement. Legacy but high-value. | Goals BETA-06, Roadmap Q2 2027 |
| Redshift connector | **Should Have (V1)** | AWS ecosystem. Common in mid-market. | Pricing §2.3 (Pro tier) |
| ClickHouse connector | **Should Have (V1)** | Analytics DB. Growing popularity. | Pricing §2.3 (Pro tier) |
| Databricks connector | **Should Have (V1)** | Part of competitive positioning. Must support Databricks users. | Pricing §2.3 (Pro tier) |
| Custom connector development service | **Should Have (V1)** | Enterprise tier. Custom integrations for specific customers. | Pricing §2.4 |
| Premium certified connectors (SAP, Oracle EBS, Salesforce) | **Could Have (V2+)** | High-value enterprise systems. Complex integration. | Business-Model §2.4 |
| 15+ database dialects | **Could Have (V2+)** | Expansion target for Phase 3. | Vision Year 2 |

---

## 5. Integrations

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Slack integration | **Should Have (V1)** | Meet users where they work. Primary adoption channel. | Goals BETA-03, Roadmap Q2 2027 |
| Microsoft Teams integration | **Should Have (V1)** | Enterprise standard. Parallel to Slack. | Goals BETA-03, Roadmap Q2 2027 |
| Tableau integration (query mining) | **Should Have (V1)** | Context enrichment from BI metadata. | Goals V1-02, Roadmap Q3 2027 |
| Looker integration (query mining) | **Should Have (V1)** | Context enrichment from BI metadata. | Goals V1-02, Roadmap Q3 2027 |
| Metabase integration (query mining) | **Should Have (V1)** | Context enrichment from BI metadata. Open-source BI. | Goals V1-02, Roadmap Q3 2027 |
| dbt integration (model import) | **Should Have (V1)** | Leverage existing semantic work. | USP §5.1, Vision Year 2 |
| MCP server (AI agent interoperability) | **Could Have (V2+)** | Future-proofing for AI agent ecosystem. | Vision §7, Market-Analysis §6 |
| Embedded API / white-label widget | **Could Have (V2+)** | Platform play. Requires mature API surface. | Business-Model §2.4, Roadmap Phase 3 |
| Marketplace (third-party connectors, packs) | **Could Have (V2+)** | Ecosystem play. Premature before product-market fit. | Business-Model §2.4, Goals ENT-04 |

---

## 6. Self-Learning

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Feedback capture + storage (corrections, approvals) | **Must Have (MVP)** | Foundation of self-learning. Capture data now, use later. | Goals MVP-07, USP §3.3 |
| Vector store for Q&A pairs | **Must Have (MVP)** | Storage layer for learning loop. Qdrant integration. | Technology-Recommendations |
| Synthetic Q&A generation for cold start bootstrap | **Should Have (V1)** | Critical for cold start. Generate from DDL + public SQL data. | Success-Metrics §5.4, Roadmap §8 |
| Active model improvement from feedback (prompt optimization) | **Should Have (V1)** | First phase of active learning. Update prompts with successful examples. | Goals BETA-05, Roadmap Q1 2027 |
| Schema enrichment from query history | **Should Have (V1)** | Mine query patterns to improve schema understanding. | Roadmap Q1-Q2 2027 |
| Feedback-collection UX (thumbs up/down + correction input) | **Should Have (V1)** | User-facing feedback mechanism. Must be unobtrusive. | Roadmap Q1 2027 |
| Learning-to-production pipeline (<24h latency) | **Should Have (V1)** | Infrastructure for continuous improvement. | Success-Metrics §5.4 |
| Model fine-tuning from accumulated feedback | **Could Have (V2+)** | Advanced learning. Requires significant data volume. | Roadmap Phase 3 |
| Customer-specific fine-tuning | **Could Have (V2+)** | Custom models per enterprise. High value, high complexity. | Goals VIS-05, Roadmap Phase 5 |

---

## 7. Analytics & Intelligence

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Dashboard builder (basic charts from SQL results) | **Should Have (V1)** | High value for business users. MVP returns table only. | Goals V1-03, Roadmap Q4 2027 |
| Scheduled reports and alerts | **Could Have (V2+)** | Proactive delivery. Requires query history baseline. | Vision Year 2 |
| Natural language reporting | **Could Have (V2+)** | "Create a weekly revenue report" → scheduled report. | Goals ENT-06, Roadmap Phase 3 |
| Data quality monitoring + anomaly detection | **Could Have (V2+)** | Additional module. Separate revenue stream. | Business-Model §2.4, Goals ENT-09 |
| Proactive anomaly alerts ("your MRR dropped 5% — here's why") | **Won't Have (Phase 3)** | Requires baseline data + mature context layer. | Roadmap Phase 4 |
| Root cause analysis ("why did revenue drop?") | **Won't Have (Phase 4)** | Multi-table, multi-query analysis. Requires cross-DB joins. | Goals PLAT-03, Roadmap Phase 4 |
| Self-driving analytics (AI finds insights without prompts) | **Won't Have (Phase 5)** | Long-term vision capability. | Goals VIS-02, Roadmap Phase 5 |
| Predictive analytics ("what will Q4 revenue be?") | **Won't Have (Phase 5)** | Forecasting capability. Requires historical data accumulation. | Goals VIS-04, Roadmap Phase 5 |
| Natural language ETL ("create pipeline joining orders and returns") | **Won't Have (Phase 5)** | Beyond current scope. Data pipeline creation is Phase 5. | Goals VIS-03, Roadmap Phase 5 |
| Natural language dashboard generation | **Should Have (V1)** | "Show me revenue by month" → dashboard. High user value. | Roadmap Q4 2027 |

---

## 8. Deployment & Infrastructure

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Multi-tenant cloud SaaS | **Must Have (MVP)** | Primary deployment mode. Tenant isolation architecture. | Technology-Recommendations |
| Kubernetes-native deployment | **Must Have (MVP)** | Cloud-agnostic, scalable infrastructure. | Technology-Recommendations |
| AMD ROCm inference support | **Must Have (MVP)** | Cost advantage. Strategic vendor independence. | Goals MVP-09, Technology-Recommendations |
| Inference abstraction layer (ROCm + CUDA + cloud APIs) | **Must Have (MVP)** | No vendor-specific code in business logic. GPU-agnostic. | Goals MVP-09 |
| Terraform IaC | **Must Have (MVP)** | Reproducible infrastructure. Cloud-agnostic. | Technology-Recommendations |
| Stateless microservices | **Must Have (MVP)** | Scalable architecture pattern. | Technology-Recommendations |
| Free tier (3 users, 100 queries/mo, PostgreSQL + DuckDB) | **Must Have (MVP)** | Self-serve evaluation. Top of funnel. | Goals MVP-06, Pricing §2.1 |
| Paid tiers + billing infrastructure | **Should Have (V1)** | Monetization. Not needed during free-tier-only MVP. | Roadmap Q1 2027 |
| Single-tenant dedicated deployment | **Should Have (V1)** | Enterprise requirement for data isolation. | Goals BETA-09 |
| Enterprise VPC deployment | **Should Have (V1)** | Customer's own cloud account. | Goals BETA-09, Roadmap Q3 2027 |
| On-premises K8s deployment | **Could Have (V2+)** | Regulated industries. High operational complexity. | Goals ENT-08, Roadmap Phase 3 |
| Air-gapped deployment (zero internet) | **Won't Have (Phase 5)** | Niche requirement (defense, intelligence). | Goals PLAT-07, Roadmap Phase 5 |

---

## 9. Authentication & User Management

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Email + password auth | **Must Have (MVP)** | Simplest auth for free tier. No SSO needed. | Roadmap MVP |
| Session management | **Must Have (MVP)** | Basic user sessions. | Roadmap MVP |
| User onboarding flow (sign up → connect DB → first query) | **Must Have (MVP)** | Critical for time-to-first-value <5min. | Success-Metrics §3.1 |
| Google/GitHub OAuth | **Should Have (V1)** | Reduce signup friction over email+password. | Common SaaS practice |
| SSO / SAML / SCIM | **Should Have (V1)** | Enterprise requirement. Cannot sell enterprise without this. | Goals BETA-04, Roadmap Q3 2027 |
| Team management (invite users, manage roles) | **Should Have (V1)** | Multi-user support for paid tiers. | Roadmap Q1 2027 |
| Custom RBAC roles | **Should Have (V1)** | Enterprise flexibility. | Pricing §2.4 |
| SCIM provisioning | **Should Have (V1)** | Enterprise IT requirement for user lifecycle management. | Goals BETA-04 |

---

## 10. Pricing & Billing

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| Free tier (usage-capped, no payment) | **Must Have (MVP)** | Self-serve evaluation. Top of funnel. | Goals MVP-06, Pricing §2.1 |
| Usage metering (count queries per seat per period) | **Should Have (V1)** | Required for billing and overage enforcement. | Business-Model §2.1 |
| Subscription billing (monthly + annual) | **Should Have (V1)** | Primary revenue collection mechanism. | Pricing §2.2-2.3 |
| Annual contract discount (~23% off monthly) | **Should Have (V1)** | Increases commitment, reduces churn. | Pricing §5 |
| Overage billing (alert + auto-top-up) | **Should Have (V1)** | Usage pricing component. | Pricing §4 |
| Self-serve upgrade (Free → Starter → Pro) | **Should Have (V1)** | PLG motion. No sales call required. | Business-Model §7 |
| Enterprise custom pricing (sales-led) | **Should Have (V1)** | Custom contracts for large customers. | Pricing §2.4 |
| Usage dashboards (for customers to track consumption) | **Could Have (V2+)** | Transparency reduces bill shock. | Pricing §4 |
| Marketplace revenue sharing | **Won't Have (Phase 3)** | Ecosystem feature. Premature. | Business-Model §2.4 |
| AI agent credits (per-call pricing) | **Won't Have (Phase 3)** | Future revenue stream. | Business-Model §2.4 |

---

## 11. Industry Verticals & Compliance

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| SOC 2 Type II certification | **Should Have (V1)** | Trust signal for enterprise. Start early. | Goals BETA-08 |
| GDPR compliance (data residency, deletion, export) | **Should Have (V1)** | European market requirement. | Problem §4.2 |
| Healthcare (HIPAA) compliance | **Could Have (V2+)** | Healthcare vertical. Higher security requirements. | Goals ENT-05 |
| Financial services (SOX) compliance | **Could Have (V2+)** | FinTech vertical. Audit requirements. | Goals ENT-05 |
| Industry-specific context models | **Could Have (V2+)** | Healthcare, finance, retail terminology. | Goals ENT-05 |

---

## 12. Developer Platform

| Feature | Priority | Rationale | Source |
|---------|----------|-----------|--------|
| REST API | **Must Have (MVP)** | API-first architecture. Enables all integrations. | Competitor Analysis §6 |
| API key management | **Should Have (V1)** | Developer access control. | Pricing §2.2-2.3 |
| API rate limiting + usage tracking | **Should Have (V1)** | Protect platform from abuse. | Pricing §2.2-2.3 |
| Webhook support (query results, alerts) | **Could Have (V2+)** | Event-driven integrations. | Developer platform growth |
| Embedded API / white-label widget | **Could Have (V2+)** | SaaS embedding. Phase 3 play. | Business-Model §2.4 |
| Open-source connector library (non-core) | **Could Have (V2+)** | Community building. Attract contributors. | Market-Analysis §9 |
| MCP server for AI agent interoperability | **Could Have (V2+)** | AI agent ecosystem. Future-proofing. | Vision §7 |

---

## 13. Summary Count

| Classification | Count | % of Total |
|---------------|-------|------------|
| **P0 — Must Have (MVP)** | 28 | 22% |
| **P1 — Should Have (V1)** | 46 | 37% |
| **P2 — Could Have (V2+)** | 30 | 24% |
| **P3 — Won't Have (for now)** | 21 | 17% |
| **Total features** | **125** | **100%** |

### MVP Feature Count by Category

| Category | Must Have | Should Have | Could Have | Won't Have |
|----------|-----------|-------------|------------|------------|
| Core NL2SQL Pipeline | 8 | 2 | 2 | 0 |
| Context Layer | 3 | 4 | 3 | 0 |
| Security & Governance | 6 | 8 | 2 | 0 |
| Database Connectors | 6 | 4 | 2 | 0 |
| Integrations | 0 | 5 | 3 | 0 |
| Self-Learning | 2 | 5 | 2 | 0 |
| Analytics & Intelligence | 0 | 2 | 2 | 6 |
| Deployment & Infrastructure | 7 | 3 | 1 | 1 |
| Auth & User Management | 3 | 4 | 0 | 0 |
| Pricing & Billing | 1 | 3 | 1 | 2 |
| Industry Verticals | 0 | 2 | 2 | 0 |
| Developer Platform | 1 | 2 | 3 | 0 |

---

## 14. Principles for Re-Prioritization

| Situation | Action |
|-----------|--------|
| Customer demands a Should Have feature during MVP | Evaluate: does it block the sale? If yes, promote to Must Have for next sprint. If no, add to roadmap with timeline. |
| Engineering discovers Must Have is 3x more complex than estimated | Evaluate: can we ship a simpler version? If not, discuss with CEO — may need to descope or delay. |
| Competitor ships a Could Have feature we planned for V2+ | Evaluate: is this a core differentiator? If yes, consider accelerating. If not, stay the course. |
| Free tier users consistently request a specific Should Have feature | Evaluate: does this improve free → paid conversion? If yes, promote priority. |
| Enterprise deal requires a feature classified as Won't Have | Evaluate: one-off custom build vs product feature. If multiple customers need it, add to roadmap. |

---

## 15. References

| Source | Relevance |
|--------|-----------|
| [Goals.md](./Goals.md) | Feature goals mapped to MVP/V1/Enterprise phases |
| [Roadmap.md](./Roadmap.md) | Timing and dependencies for each feature |
| [Vision.md](./Vision.md) | Long-term feature evolution and North Star alignment |
| [USP.md](./USP.md) | Differentiating features vs "table stakes" features |
| [Pricing.md](./Pricing.md) | Feature availability by pricing tier |
| [Customer-Personas.md](./Customer-Personas.md) | Feature priority by persona need |
| [Competitor-Analysis.md](./Competitor-Analysis.md) | Competitive feature parity requirements |
