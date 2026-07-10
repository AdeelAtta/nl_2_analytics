# Customer Personas

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Problem.md](./Problem.md), [Market-Analysis.md](./Market-Analysis.md), [Vision.md](./Vision.md) |

---

## 1. Primary Persona: Head of Data / Director of Analytics

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | Head of Data, Director of Analytics, VP Data |
| **Company Size** | 100-5,000 employees |
| **Team Size** | 3-20 data analysts, 1-5 data engineers |
| **Database Count** | 3-20 databases (Postgres, Snowflake, BigQuery, MySQL, etc.) |
| **Tech Stack** | dbt, Snowflake, Metabase/Tableau, Fivetran, Airflow |
| **Annual Budget** | $500K-$5M (data team + infrastructure) |
| **Reporting To** | CTO, VP Engineering, or CEO |

### Pain Points

| # | Pain Point | Severity | Frequency |
|---|-----------|----------|-----------|
| P1 | Analysts spend 40-60% of time on routine SQL; can't focus on high-value work | Critical | Daily |
| P2 | Business stakeholders file Jira tickets for simple queries; 2-5 day turnaround | Critical | Daily |
| P3 | No single person understands all 10+ databases; tribal knowledge walks out the door | High | Monthly |
| P4 | Onboarding new analysts takes 2-4 weeks just to learn the schemas | High | Quarterly |
| P5 | Can't scale the team — hiring more analysts doesn't solve the bottleneck | High | Quarterly |
| P6 | Business users demand self-serve analytics but existing BI tools require too much setup | Medium | Monthly |

### Goals

| # | Goal | Priority | Success Metric |
|---|------|----------|----------------|
| G1 | Reduce analyst time on routine queries by 50%+ | Critical | Hours saved/week |
| G2 | Enable business stakeholders to answer their own simple questions | Critical | % of tickets deflected |
| G3 | Create a single source of truth for business data understanding | High | New analyst onboarding time |
| G4 | Improve data-driven decision-making velocity | High | Decision turnaround time |
| G5 | Justify data team ROI to executive leadership | Medium | Self-service adoption metrics |

### Buying Journey

| Stage | Activity | Time |
|-------|----------|------|
| **Awareness** | Sees demo at data conference, reads engineering blog, hears from peer | 0-30 days |
| **Evaluation** | Signs up for free tier, connects a non-production database, tests 10 queries | 30-60 days |
| **Pilot** | Connects one production database (e.g., Postgres), 5 user trial | 60-90 days |
| **Purchase** | Negotiates annual contract, security review, legal approval | 90-180 days |
| **Rollout** | Connects all databases, 50-200 user rollout, training | 180-270 days |

### Decision Criteria (Ranked)

| # | Criterion | Weight |
|---|-----------|--------|
| 1 | Accuracy on our specific schemas | 30% |
| 2 | Ease of setup (no manual modeling) | 20% |
| 3 | Security and RBAC | 15% |
| 4 | Cross-database support | 15% |
| 5 | Price / ROI justification | 10% |
| 6 | Integration with existing stack | 10% |

### Quote

> "I have 8 analysts and 100+ pending data requests. If I could eliminate 50% of the SQL busywork, I could double our analytical output without hiring anyone."

---

## 2. Primary Persona: Analytics Engineer / Senior Data Analyst

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | Analytics Engineer, Senior Data Analyst, Data Scientist |
| **Company Size** | 200-5,000 employees |
| **Experience** | 3-10 years SQL + BI tools |
| **SQL Proficiency** | Advanced (can write complex multi-join queries) |
| **Frustration** | Writing the same `SELECT ... GROUP BY ... ORDER BY ...` queries repeatedly |

### Pain Points

| # | Pain Point | Severity |
|---|-----------|----------|
| P1 | 60% of work is routine queries that a junior could write | Critical |
| P2 | Frequently interrupted by stakeholders asking "can you run me a quick query?" | Critical |
| P3 | Business glossary doesn't exist; every metric needs re-explanation | High |
| P4 | Spends 2-4 weeks learning new schemas when joining a company | High |
| P5 | Documentation is always out of date | Medium |

### Goals

| # | Goal |
|---|------|
| G1 | Focus on high-value work: data modeling, experimentation, strategy |
| G2 | Empower stakeholders to self-serve without compromising data quality |
| G3 | Build and maintain the business context layer (not write ad hoc queries) |
| G4 | Reduce context-switching from interruptions |

### How They Evaluate

| Criterion | Importance |
|-----------|------------|
| Does it get the SQL right on our messy schemas? | Highest |
| Can I trust the output without manually verifying? | High |
| Does it learn from my corrections? | High |
| Can I see and edit the generated SQL? | Medium |
| Does it integrate with our existing tools? | Medium |

### Quote

> "I became a data analyst to find insights, not to type `SELECT` from 15 different tables every day. If the AI handles the boilerplate, I can actually think about the business."

---

## 3. Primary Persona: CTO / VP Engineering

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | CTO, VP Engineering, Chief Data Officer |
| **Company Size** | 100-2,000 employees |
| **Focus** | Architecture, scalability, security, team efficiency |
| **Concern** | Data quality, governance, unauthorized data access |

### Pain Points

| # | Pain Point | Severity |
|---|-----------|----------|
| P1 | Slow decision-making because data is hard to access | Critical |
| P2 | Data team is a bottleneck; can't recruit fast enough | Critical |
| P3 | No visibility into who is accessing what data | High |
| P4 | Multiple databases with no unified understanding | High |
| P5 | Audit and compliance requirements not met by existing tools | Medium |

### Goals

| # | Goal |
|---|------|
| G1 | Democratize data access while maintaining governance |
| G2 | Reduce data team hiring needs by 30%+ through self-serve |
| G3 | Get full audit trail of all data queries |
| G4 | Ensure security compliance (SOC 2, GDPR, HIPAA) |
| G5 | Scale data capabilities without proportional cost increase |

### Buying Concerns

| Concern | Question |
|---------|----------|
| Security | "Can this leak sensitive data?" |
| Control | "Can I restrict access per user/role/column?" |
| Accuracy | "Will wrong answers cause bad decisions?" |
| Vendor lock-in | "Can I run it on-prem if needed?" |
| Cost | "Does ROI justify the spend?" |

### Quote

> "I need my team answering business questions, not tickets. If this cuts the SQL overhead by half, it pays for itself in two months."

---

## 4. Secondary Persona: Product Manager

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | Product Manager, Group PM, Director of Product |
| **Company Size** | 200-5,000 employees |
| **SQL Proficiency** | Basic (can read SQL, write simple queries) |
| **Data Need** | 3-10 ad hoc queries per week for decisions |

### Pain Points

| # | Pain Point | Severity |
|---|-----------|----------|
| P1 | Has to wait 2-5 days for every data question | Critical |
| P2 | Can't explore data iteratively ("what if I also look at...") | High |
| P3 | Dashboard covers 80% of needs; the remaining 20% requires a Jira ticket | High |
| P4 | Doesn't know what questions are possible to ask | Medium |

### How They Use the Product

1. Asks question in natural language
2. Gets answer + SQL + visualization in <5 seconds
3. Iterates with follow-up questions
4. Saves useful queries for the team
5. Rarely looks at the SQL — trusts the system

### Quote

> "I know what question I want to ask. I just don't know how to write the SQL. And I shouldn't have to — I'm not a data analyst."

---

## 5. Secondary Persona: Business Analyst

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | Business Analyst, Operations Analyst, Marketing Analyst |
| **Company Size** | 500-5,000 employees |
| **SQL Proficiency** | None to basic |
| **Current Tools** | Excel, pre-built dashboards, manual reports |

### Pain Points

| # | Pain Point | Severity |
|---|-----------|----------|
| P1 | Limited to pre-built dashboards; can't explore beyond them | Critical |
| P2 | Manual data pulls from multiple sources take hours | Critical |
| P3 | Different data sources define metrics differently | High |
| P4 | No easy way to ask follow-up questions | High |

### Quote

> "I spend 3 hours every Monday pulling data from 4 different systems into a spreadsheet. If I could just ask and get the answer, I'd save half my week."

---

## 6. Secondary Persona: C-Suite Executive

### Demographics

| Attribute | Value |
|-----------|-------|
| **Title** | CEO, CFO, COO |
| **Company Size** | 500-10,000 employees |
| **SQL Proficiency** | None |
| **Data Need** | 1-5 strategic questions per week |

### Pain Points

| # | Pain Point | Severity |
|---|-----------|----------|
| P1 | Can't get quick answers to strategic questions | Critical |
| P2 | Different departments report the same metric differently | High |
| P3 | Doesn't trust data quality from self-serve tools | High |

### Quote

> "I asked three VPs the same question and got three different answers. I need one source of truth I can trust."

---

## 7. Buying Center Map

```
                      C-Suite Executive
                     (Budget Approver)
                           │
                           ▼
                    Head of Data / CDO
                   (Primary Buyer / Champion)
                    │          │          │
                    ▼          ▼          ▼
           Analytics Eng   Data Analyst   Data Engineer
           (Power User)    (Power User)   (Integration)
                    │          │          │
                    └──────────┼──────────┘
                               │
                               ▼
                          CTO / VP Eng
                       (Technical Evaluator)
                               │
                               ▼
                     Security / Compliance
                       (Gatekeeper)
```

### Influencer Dynamics

| Role | Influence | Role in Decision | Objection If... |
|------|-----------|------------------|-----------------|
| Head of Data | High | Champion, evaluates fit | Accuracy < 80% on their schemas |
| Analyst | Medium | Power user, validates | Can't see/edit SQL |
| CTO | High | Technical decision | Security concerns |
| Security | High (veto) | Compliance review | Data exfiltration risk |
| CFO | High (budget) | Budget approval | ROI not clear |
| CEO | Medium | Vision alignment | Not enterprise-ready |

---

## 8. Adoption Journey

### Phase 1: The Skeptical Analyst

> "I don't trust AI to write SQL. I'll try it on a non-critical database."

**Trigger**: A stakeholder request backlog > 20 items

**Success moment**: First query that returns exactly what they would have written — in 3 seconds instead of 15 minutes.

### Phase 2: The Power User

> "OK, this works for simple queries. Let me try it on something harder."

**Trigger**: Saves 5+ hours in the first week

**Success moment**: System correctly generates a 7-table join with window functions that would take 30 minutes to write manually.

### Phase 3: The Champion

> "I'm telling my team about this. Every analyst should use it."

**Trigger**: 50+ queries answered with <5% needing correction

**Success moment**: Recommends purchase to Head of Data.

### Phase 4: The Organization

> "This is now our primary data access layer. We're connecting all databases."

**Trigger**: 10+ power users, 50+ business users, measurable time savings

**Success moment**: Analyst ticket queue shrinks by 60%+.

---

## 9. Key Insights for Product Decisions

| Insight | Implication |
|---------|-------------|
| Analysts want to see/edit SQL; business users don't | Show SQL by default for analysts, hide for business users |
| Cold start accuracy determines adoption | Must achieve >70% accuracy on first use (no training data) |
| Trust is built through transparency | Show reasoning, confidence, alternatives |
| Security is the #1 dealbreaker | Enterprise features are table stakes, not differentiators |
| Integration depth drives retention | Slack, Teams, dbt, Metabase, Tableau connectors are essential |
| Mid-market needs self-serve sales | Free tier → paid conversion must be product-led |

---

## 10. References

| Source | Relevance |
|--------|-----------|
| [Problem.md](./Problem.md) | Pain points this persona experiences |
| [Market-Analysis.md](./Market-Analysis.md) | Market size by persona segment |
| [Vision.md](./Vision.md) | How the product addresses each persona's needs |
| Basedash NL2SQL tools survey (2026) | User priorities for NL2SQL tool selection |
| dbt Labs benchmark (2026) | Analyst preferences for SQL visibility |
| Cisco NL2SQL case study (2025) | Enterprise analyst adoption journey |
