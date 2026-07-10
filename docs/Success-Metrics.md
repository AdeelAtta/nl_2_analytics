# Success Metrics

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Goals.md](./Goals.md), [Business-Model.md](./Business-Model.md), [Roadmap.md](./Roadmap.md) |

---

## 1. Metric Framework

We organize success metrics into four categories using **OKR-style ownership**:

| Category | Owner | Purpose |
|----------|-------|---------|
| Business KPIs | CEO / Sales | Company health, growth, revenue |
| Product KPIs | CPO / Product | Adoption, engagement, retention |
| Engineering KPIs | CTO / Eng | Quality, performance, reliability |
| AI KPIs | ML Team | Accuracy, safety, efficiency |

---

## 2. Business KPIs

### 2.1 Revenue & Growth

| Metric | Target (Year 1) | Target (Year 3) | Stretch |
|--------|----------------|-----------------|---------|
| ARR | $450K | $17.5M | $25M |
| Net Revenue Retention (NRR) | >110% | >120% | >140% |
| Gross Margin | >70% | >85% | >90% |
| CAC (mid-market) | <$2K | <$1K | <$500 |
| LTV:CAC (mid-market) | >5:1 | >10:1 | >15:1 |
| LTV:CAC (enterprise) | >3:1 | >5:1 | >8:1 |
| Monthly Recurring Revenue (MRR) | $37.5K | $1.46M | $2.1M |

### 2.2 Customer Acquisition

| Metric | Target (Year 1) | Target (Year 3) | Stretch |
|--------|----------------|-----------------|---------|
| Paying customers | 25 | 500 | 750 |
| Free → paid conversion | 3% | 5% | 8% |
| Enterprise deals (>$25K ACV) | 5 | 50 | 100 |
| Customer acquisition cost (enterprise) | <$50K | <$25K | <$15K |

---

## 3. Product KPIs

### 3.1 Adoption & Engagement

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Weekly active users (WAU) / Total users | >60% | Product analytics |
| Queries per active user per week | >15 | After initial 4-week ramp |
| Time to first query | <5 minutes | From account creation |
| Time to first value | <24 hours | Schema automatically understood |
| Feature adoption (context layer) | >80% of active users | % using context overlays |
| Integration adoption | >50% of teams connect ≥2 DBs | Connection count |
| Slack / Teams integration | >40% daily active | Message count |

### 3.2 Retention

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| D30 retention | >80% | Users active on day 30 |
| D90 retention | >60% | Users active on day 90 |
| Monthly churn (mid-market) | <5% | Billing churn |
| Annual churn (enterprise) | <10% | Contract renewal |
| Net revenue retention | >110% | Expansion / contraction |

### 3.3 NPS & Satisfaction

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| NPS | >40 | Quarterly survey |
| CSAT (support) | >90% | Post-ticket survey |
| Feature request satisfaction | >70% | % of top 10 requests shipped within 90 days |

---

## 4. Engineering KPIs

### 4.1 Reliability

| Metric | Target | SLA |
|--------|--------|-----|
| Uptime (cloud) | 99.9% | 99.5% (Starter) / 99.9% (Pro) |
| API P50 latency | <500ms | Query to SQL generation |
| API P95 latency | <3s | Including database execution |
| API P99 latency | <10s | Including complex queries |
| Error rate (query failures) | <1% | Non-user-error failures |
| Mean time to recovery (MTTR) | <15 minutes | Production incidents |

### 4.2 Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Query generation (P95) | <2s | From natural language to SQL |
| Query execution (P95) | <5s | Including DB execution time |
| Context discovery time (100 tables) | <1 minute | First-time schema analysis |
| Context refresh time (1,000 tables) | <5 minutes | Incremental |
| Embedding generation throughput | >100 texts/second | Per GPU |
| Concurrent users per node | >50 | Standard K8s pod size |

### 4.3 Quality

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Deploy frequency | Weekly (Year 1) → Daily (Year 3+) | CI/CD pipeline |
| Change failure rate | <5% | Deployments causing incidents |
| Test coverage | >80% | Code coverage tools |
| Security vulnerability count | 0 critical | Regular scanning |
| Crash-free session rate | >99.5% | Client-side telemetry |

---

## 5. AI KPIs

### 5.1 Accuracy

| Metric | Target | Target Definition |
|--------|--------|-------------------|
| Semantic accuracy (SQL correctness) | >85% | Execution-pass rate on known queries |
| Business accuracy (answers the right question) | >80% | Human evaluation of result relevance |
| First-query success rate | >70% | No follow-up correction needed |
| Context retrieval precision@10 | >0.90 | Relevant tables/columns in top 10 |
| Context retrieval recall@10 | >0.85 | All relevant tables in top 10 |
| Schema element discovery rate | >95% | % of tables/columns discovered automatically |

**Measurement approach**:
- **Week 1-12**: Synthetic benchmarks (Spider 2.0, BIRD-SQL)
- **Week 13+**: Production query logging + manual sampling for accuracy
- **Quarterly**: Human evaluation of 500 sampled queries against ground truth

### 5.2 Safety

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Guardrail false positive rate | <1% | Legitimate queries blocked |
| Guardrail false negative rate | <0.1% | Dangerous queries allowed |
| PII detection accuracy | >99% | On standard PII benchmarks |
| SQL injection prevention | 100% | Automated injection testing |
| Audit log completeness | 100% | Log vs actual query comparison |

### 5.3 Efficiency

| Metric | Target | Rationale |
|--------|--------|-----------|
| Cache hit rate | >40% | Reduce redundant computation |
| Average inference cost per query | <$0.01 | Target for profitability |
| Self-hosted inference % | >95% | Minimize cloud API costs |
| Model routing accuracy | >90% | Correct tier selection for query complexity |
| Learning loop contribution | >5% accuracy improvement/month | After cold start |

### 5.4 Self-Learning Loop

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Feedback collection rate | >10% of queries | User corrects/approves result |
| Learning-to-production latency | <24 hours | Time from feedback to model improvement |
| Accuracy improvement (monthly) | >2% | Per-cohort query accuracy over time |
| Cold start duration | <30 days | Time to achieve >70% first-query success |
| Synthetic Q&A quality (human eval) | >80% acceptable | Sampled evaluation |

---

## 6. Security & Compliance

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| SOC 2 Type II readiness | Achieved by Phase 2 | External auditor |
| Penetration test pass rate | 100% critical/high | Quarterly pen test |
| Vulnerability remediation time (critical) | <24 hours | From disclosure to patch |
| Data encryption (at rest / in transit) | 100% | Verified by scanning |
| Access control audit pass rate | 100% | Quarterly access review |

---

## 7. Leading vs Lagging Indicators

| Type | Metric | Why |
|------|--------|-----|
| **Leading** | Free tier signups | Predicts future pipeline |
| **Leading** | Free → trial conversion | Predicts future paid conversions |
| **Leading** | D30 retention | Predicts long-term retention |
| **Leading** | Queries per user per week | Predicts value perception |
| **Leading** | Context layer discovery rate | Predicts accuracy improvement |
| **Lagging** | ARR | Ultimate business health |
| **Lagging** | Churn rate | Past retention issues |
| **Lagging** | NPS | Past satisfaction |
| **Lagging** | Gross margin | Past economic efficiency |

---

## 8. Metric Frequency

| Frequency | Metrics | Purpose |
|-----------|---------|---------|
| Real-time | Uptime, latency, error rate, policy enforcement events | Operational health |
| Daily | Active users, queries, new signups, feedback | Engagement tracking |
| Weekly | Conversions, trials, churn precursors, accuracy sample | Leading indicators |
| Monthly | ARR, NRR, churn, CAC, gross margin, accuracy trend | Business health |
| Quarterly | NPS, pen test results, human accuracy evaluation, OKR review | Strategic direction |

---

## 9. Metric Ownership

| Role | Owns | Reviews |
|------|------|---------|
| CEO | ARR, NRR, CAC, LTV:CAC | Monthly board |
| CTO | Uptime, latency, error rates, deploy frequency | Daily standup |
| ML Lead | Accuracy, safety, efficiency, learning metrics | Weekly AI review |
| Head of Product | Adoption, retention, NPS, conversion | Weekly product review |
| Head of Sales | Pipeline, win rate, ACV, enterprise deals | Weekly sales review |

---

## 10. Metric Dependencies

```
Accuracy → Retention (higher accuracy → lower churn)
Latency → Adoption (faster queries → more usage)
Context coverage → Accuracy (better context → more correct queries)
Guardrail accuracy → Trust (fewer false positives → more adoption)
Self-learning → Accuracy (more feedback → better over time)
Adoption → Feedback volume (more usage → more learning data)
Accuracy → Revenue (better product → higher willingness to pay)
```

---

## 11. References

| Source | Relevance |
|--------|-----------|
| [Goals.md](./Goals.md) | Milestones tied to metric achievements |
| [Business-Model.md](./Business-Model.md) | Revenue and cost metrics |
| [Roadmap.md](./Roadmap.md) | Metric targets by phase |
| a16z "SaaS Metrics 2.0" (2025) | Modern SaaS metric frameworks |
| OpenView "SaaS Benchmarks" (2025) | Industry comparison baselines |
| Lenny Rachitsky "Product Metrics" (2024) | Product engagement metrics |
