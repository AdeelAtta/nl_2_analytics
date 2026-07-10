# Goals

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Roadmap.md](./Roadmap.md), [Vision.md](./Vision.md), [Success-Metrics.md](./Success-Metrics.md) |

---

## 1. Goal Structure

Each goal follows the **SMART** framework:

| Letter | Meaning | Our Translation |
|--------|---------|----------------|
| **S**pecific | Clear, unambiguous | One sentence, no interpretation needed |
| **M**easurable | Quantifiable | One numeric target |
| **A**chievable | Realistic | Evidence it's possible |
| **R**elevant | Aligns with strategy | Traceable to Vision/Mission |
| **T**ime-bound | Has a deadline | Date or quarter |

---

## 2. MVP Goals (Phase 1 — Q3-Q4 2026)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| MVP-01 | **Working single-DB NL2SQL** — A user can type "show me revenue by month for 2025" and receive correct SQL + results | 10 benchmark queries produce correct SQL (execution-pass) against PostgreSQL | P0 |
| MVP-02 | **Autonomous context discovery** — Platform auto-discovers schema + business meaning for a 100-table database without human input | DDL parsed, table relationships inferred, business names extracted in < 5 minutes | P0 |
| MVP-03 | **Security guarantee** — No query can modify, delete, or access unauthorized data | 100% pass on 100 test injection/quarantine scenarios | P0 |
| MVP-04 | **Multi-database querying** — User can query 5 database dialects (PG, MySQL, Snowflake, BigQuery, DuckDB) | Same natural language query works across all 5 dialects | P0 |
| MVP-05 | **Tiered model routing** — SQLCoder-7b handles simple queries, Qwen2.5-72B medium, DeepSeek-V3 complex | Router selects correct model > 85% of the time; cost per query < $0.01 | P0 |
| MVP-06 | **Free tier live** — Anyone can sign up, connect a database, and ask questions | 100 free tier signups in first month post-launch | P1 |
| MVP-07 | **Self-learning loop foundation** — User corrections and approvals are captured and stored for retraining | Feedback collection rate > 5% of queries | P1 |
| MVP-08 | **Query history** — Every query + result + user action is logged and viewable | Full audit trail, searchable within 5 seconds | P1 |
| MVP-09 | **Inference abstraction layer** — Platform runs on AMD ROCm, with cloud API fallback | Same code path, no vendor-specific calls in business logic | P0 |

---

## 3. Beta Goals (Phase 2 — Q1-Q2 2027)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| BETA-01 | **25 paying customers on Starter/Pro tiers** | 25 customers with ACV > $5K | P0 |
| BETA-02 | **RBAC + column-level security** | Admin can define roles that restrict specific columns; enforced in all queries | P0 |
| BETA-03 | **Slack/Teams integration** | User sends "revenue by month" in Slack → gets SQL + chart back | P0 |
| BETA-04 | **SSO/SAML/SCIM** | Enterprise can onboard users via existing identity provider | P0 |
| BETA-05 | **Self-learning improvement measurable** | Accuracy improves > 5% month-over-month from feedback loop | P1 |
| BETA-06 | **SQL Server + Oracle connectors** | Both drivers tested with 10+ stored procedures each | P1 |
| BETA-07 | **Customer NPS > 30** | Beta user survey | P1 |
| BETA-08 | **SOC 2 Type II readiness** | External auditor confirms controls | P0 |
| BETA-09 | **Enterprise dedicated deployment** | First customer running in their VPC | P1 |
| BETA-10 | **Query generation P95 < 2s** | Performance target met | P1 |

---

## 4. V1 Goals (Phase 2 — Q3-Q4 2027)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| V1-01 | **150 paying customers** ($3.75M ARR) | 100 mid-market + 50 enterprise | P0 |
| V1-02 | **Context layer V2 — BI tool integration** | Queries from Tableau/Looker/Metabase feed context | P0 |
| V1-03 | **Dashboard builder** | User can save queries as charts, arrange into dashboards | P1 |
| V1-04 | **Learned model routing** | Router improves from production data; routing accuracy > 90% | P2 |
| V1-05 | **Audit log SIEM integration** | Customers can stream audit logs to Splunk/Datadog | P1 |
| V1-06 | **99.9% uptime** (Pro tier) | Monthly SLA met | P0 |
| V1-07 | **Net revenue retention > 110%** | Existing customers expand | P0 |
| V1-08 | **10 enterprise customers > $50K ACV** | Enterprise sales motion validated | P1 |
| V1-09 | **Self-hosted inference > 95%** | Cloud API calls < 5% of total | P1 |
| V1-10 | **Accuracy > 85% on production queries** | Human-evaluated sample of 500 queries | P0 |

---

## 5. Enterprise Goals (Phase 3 — 2028)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| ENT-01 | **$17.5M ARR** | 500 customers | P0 |
| ENT-02 | **Cross-database joins** | One question joins PostgreSQL + Snowflake + BigQuery | P0 |
| ENT-03 | **Embedded API live** | 5 SaaS products embed our NL2SQL widget | P1 |
| ENT-04 | **Marketplace launched** | 10 third-party connector/semantic packs available | P2 |
| ENT-05 | **Industry vertical solutions** | Healthcare (HIPAA), Finance (SOX), Retail | P1 |
| ENT-06 | **Natural language dashboarding** | "Create a monthly revenue dashboard" → dashboard exists | P1 |
| ENT-07 | **Gross margin > 85%** | Inference costs scaled efficiently | P0 |
| ENT-08 | **On-prem K8s deployment operational** | First on-prem customer | P2 |
| ENT-09 | **Data quality monitoring module** | Anomaly detection for key metrics | P2 |
| ENT-10 | **NPS > 50** | Customer satisfaction | P1 |

---

## 6. Platform Goals (Phase 4 — 2029)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| PLAT-01 | **$54M ARR** | 1,200 customers | P0 |
| PLAT-02 | **Proactive insights** | AI alerts on anomalies without prompts | P0 |
| PLAT-03 | **Root cause analysis** | "Why did revenue drop?" → multi-table analysis | P0 |
| PLAT-04 | **Natural language reporting** | Scheduled NL-generated reports | P1 |
| PLAT-05 | **Multi-model queries** | SQL + vector + graph in single question | P2 |
| PLAT-06 | **Gross margin > 90%** | Optimized infrastructure | P1 |
| PLAT-07 | **Air-gapped deployment readiness** | Architecture validated | P2 |

---

## 7. Vision Goals (Phase 5 — 2030)

| ID | Goal | Success Criteria | Priority |
|----|------|-----------------|----------|
| VIS-01 | **$137M ARR** | 2,500 customers | P0 |
| VIS-02 | **Self-driving analytics** | AI surfaces insights proactively, fully autonomous | P0 |
| VIS-03 | **Natural language ETL** | "Create pipeline joining orders and returns" | P0 |
| VIS-04 | **Predictive analytics** | "What will Q4 revenue be?" with trend analysis | P1 |
| VIS-05 | **Custom customer fine-tuning** | Customer trains model on their schema patterns | P2 |
| VIS-06 | **BI tool replacement** | Full analytics platform, replaces traditional BI | P1 |
| VIS-07 | **Air-gapped deployment** | Zero internet dependency | P2 |

---

## 8. Goal Dependencies

```
MVP-01 (single-DB NL2SQL) ──► MVP-04 (multi-DB) ──► BETA-01 (25 customers)
MVP-02 (context discovery) ──► MVP-04 (multi-DB) ──► V1-02 (BI context)
MVP-03 (security) ──► BETA-02 (RBAC) ──► ENT-05 (industry verticals)
MVP-05 (tiered routing) ──► V1-04 (learned routing) ──► ENT-07 (gross margin)
MVP-07 (learning loop) ──► BETA-05 (self-learning) ──► V1-10 (accuracy)
BETA-04 (SSO) ──► BETA-09 (enterprise VPC) ──► ENT-08 (on-prem)
V1-03 (dashboard) ──► ENT-06 (NL dashboarding) ──► VIS-06 (BI replacement)
ENT-02 (cross-DB joins) ──► PLAT-03 (root cause) ──► VIS-02 (self-driving)
```

---

## 9. Metric Gates Between Phases

| From | To | Required Metric Achievement |
|------|----|---------------------------|
| MVP | Beta | 9/9 MVP goals met (MVP-01 through MVP-09 all pass) |
| Beta | V1 | 25 paying customers, NPS > 30, accuracy > 75% |
| V1 | Enterprise | 200 customers, NRR > 110%, accuracy > 85% |
| Enterprise | Platform | $17.5M ARR, gross margin > 85%, cross-DB joins functional |
| Platform | Vision | $54M ARR, proactive insights live |

---

## 10. Goals Review Cadence

| Cadence | Reviews | By |
|---------|---------|-----|
| Weekly | Task-level progress against current phase goals | CTO / PM |
| Monthly | Phase goal completion %, blockers identified | Leadership |
| Quarterly | Phase transition decision (Go / No-Go) | Founders + Board |
| Annually | Overall strategy alignment, five-year refresh | Founders |

---

## 11. What Success Looks Like

### By End of 2026 (MVP)
> A mid-market company can sign up, connect their PostgreSQL database, and within 5 minutes be asking natural language questions with accurate SQL answers. The system automatically understands their schema without configuration. They trust it because every query is guaranteed read-only and audited.

### By End of 2027 (V1)
> A regulated enterprise with 50+ users across Snowflake, PostgreSQL, and SQL Server is running daily operations through our platform. The system has learned their domain language over 6 months and is noticeably more accurate than when they started. Their SOC 2 audit passes with no controls gaps.

### By 2030 (Vision)
> A Fortune 500 company runs their entire analytics infrastructure through our platform. The AI proactively discovers insights, performs root cause analysis, and generates reports. They have not hired a new data analyst in 2 years because the platform replaced 60% of their workload. Their data team now focuses on strategy, not SQL.

---

## 12. References

| Source | Relevance |
|--------|-----------|
| [Roadmap.md](./Roadmap.md) | Timeline and milestones for each goal |
| [Success-Metrics.md](./Success-Metrics.md) | Detailed measurement of each goal |
| [Vision.md](./Vision.md) | Long-term north star alignment |
| [Business-Model.md](./Business-Model.md) | Revenue targets tied to customer acquisition goals |
