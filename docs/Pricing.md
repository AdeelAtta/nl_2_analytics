# Pricing

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Business-Model.md](./Business-Model.md), [Market-Analysis.md](./Market-Analysis.md), [Competitor-Analysis.md](./Competitor-Analysis.md) |

---

## 1. Pricing Philosophy

Our pricing strategy is built on four principles:

| Principle | Meaning | Implementation |
|-----------|---------|---------------|
| **Value-based** | Price relative to value (analyst time saved), not cost | $50/seat = 1% of analyst salary |
| **Simple** | Easy to understand, no hidden fees | Two core tiers + enterprise |
| **Predictable** | Customers know their monthly cost | Annual contracts, capped usage |
| **Scalable** | Pricing grows with customer value | Seat + usage; enterprise at scale |

---

## 2. Pricing Tiers

### 2.1 Free Tier

| Component | Detail |
|-----------|--------|
| **Price** | $0 |
| **Seats** | 3 users |
| **Queries per month** | 100 total |
| **Databases** | 1 |
| **Databases supported** | PostgreSQL, DuckDB |
| **Context layer** | Basic (DDL-based only, no query history mining) |
| **Support** | Community (GitHub issues, Discord) |
| **SLA** | None |
| **Purpose** | Evaluation, individual users, proof of concept |

### 2.2 Starter Tier

| Component | Detail |
|-----------|--------|
| **Price** | **$50/seat/month** (annual) / **$65/seat/month** (monthly) |
| **Minimum seats** | 5 |
| **Queries per seat/month** | 200 included ($0.25/query overage) |
| **Databases** | Up to 3 |
| **Databases supported** | PostgreSQL, MySQL, Snowflake, BigQuery, DuckDB |
| **Context layer** | Standard (DDL + query history + basic docs) |
| **Slack / Teams integration** | Yes |
| **API access** | Yes (1,000 API calls/hour limit) |
| **Support** | Email + chat (business hours) |
| **SLA** | 99.5% uptime |
| **Target customer** | 5-25 person data teams, single-platform or 2-3 databases |

### 2.3 Pro Tier

| Component | Detail |
|-----------|--------|
| **Price** | **$150/seat/month** (annual) / **$195/seat/month** (monthly) |
| **Minimum seats** | 10 |
| **Queries per seat/month** | 1,000 included ($0.15/query overage) |
| **Databases** | Up to 10 |
| **Databases supported** | All supported (PostgreSQL, MySQL, Snowflake, BigQuery, SQL Server, Oracle, Redshift, ClickHouse, Databricks, DuckDB) |
| **Context layer** | Full (DDL + query history + docs + BI integration + self-learning) |
| **RBAC** | Role-based access control |
| **Column-level security** | Yes |
| **Audit trail** | Full, searchable, exportable |
| **Slack / Teams integration** | Yes |
| **API access** | Yes (10,000 API calls/hour limit) |
| **Embedded widgets** | Yes (up to 5) |
| **Support** | Priority email + chat + video (business hours) |
| **SLA** | 99.9% uptime |
| **Target customer** | 25-100 person organizations, multi-database, require governance |

### 2.4 Enterprise Tier

| Component | Detail |
|-----------|--------|
| **Price** | **Custom** (starting at $25K/year) |
| **Seats** | Unlimited |
| **Queries** | Custom (unlimited available) |
| **Databases** | Unlimited |
| **Databases supported** | All supported + custom connector development |
| **Deployment options** | Cloud (dedicated), VPC, on-premises |
| **SSO / SAML** | Yes |
| **Custom RBAC** | Yes (custom roles, SCIM) |
| **Audit** | Immutable, encrypted, SIEM integration |
| **SLA** | 99.95% uptime (cloud) / custom (on-prem) |
| **Support** | 24/7, dedicated account manager, 2-hour response |
| **Professional services** | Included (up to 20 days/year) |
| **Custom integrations** | Yes |
| **Target customer** | 500+ employee organizations, regulated industries, complex environments |

---

## 3. Pricing Comparison

### 3.1 Versus Alternatives

| Product | 10 Users | 50 Users | 200 Users | Key Difference |
|---------|----------|----------|-----------|----------------|
| **Our Platform (Pro)** | **$1,500/mo** | **$7,500/mo** | **$30,000/mo** | Autonomous setup, cross-DB |
| Snowflake Cortex Analyst | Included in $2K-10K/mo compute | Same | Same | Snowflake-only, manual YAML |
| Databricks Genie | Included in $1K-5K/mo DBUs | Same | Same | Databricks-only, curated setup |
| Vanna AI | $500/mo | $2,500/mo | $10,000/mo | Library, requires engineering |
| WrenAI | $990/mo | $4,950/mo | $19,800/mo | Requires MDL modeling |
| Seek AI | Custom $50K+/yr | Custom $50K+/yr | Custom $100K+/yr | Enterprise-only pricing |
| ThoughtSpot | N/A | N/A | $100K+/yr | Months of setup |

### 3.2 ROI Calculation

| Role | Annual Cost | Hours/Week on SQL | Tool Savings | Tool Cost | Net Savings |
|------|-------------|-------------------|-------------|-----------|-------------|
| Data Analyst | $120K | 24 hours (60%) | $72K (50% reduction) | $1,800/yr ($150/mo) | **$70,200** |
| Product Manager | $150K | 5 hours | $37.5K (50% reduction) | $1,800/yr | **$35,700** |
| Business Analyst | $90K | 15 hours | $33.75K (50% reduction) | $1,800/yr | **$31,950** |

**Conclusion**: At $150/seat/month, the tool pays for itself in **days** for any role that regularly queries data.

---

## 4. Overage Pricing

| Tier | Overage Rate | Purpose |
|------|-------------|---------|
| Starter | $0.25/query | Prevent abuse, not a revenue driver |
| Pro | $0.15/query | Covers inference costs + margin |
| Enterprise | Custom/Negotiated | Typically unlimited or high cap |

**Design principle**: Overage should not surprise customers. Alert at 75%, 90%, and 100% of included queries. Offer auto-top-up in increments of 500 or 1,000 queries.

---

## 5. Discount Structure

| Discount | Eligibility | Amount |
|----------|-------------|--------|
| Annual commitment | All paid tiers | ~23% off monthly price |
| Non-profit / education | Verified organizations | 40% off |
| Startup (<$5M ARR) | Pro tier, first year | 30% off |
| Volume (50+ seats) | Pro tier | 10% off |
| Volume (200+ seats) | Pro tier | 20% off |
| Multi-year (2+ years) | Enterprise | 10-20% off |
| Reference customer | Willing case study participant | 20% off first year |

---

## 6. Pricing Changes Over Time

| Phase | Pricing Strategy | Rationale |
|-------|-----------------|-----------|
| MVP (Year 1) | Lower to gain traction | Free tier generous, Starter at $35/seat intro |
| Growth (Year 2) | Increase to standard rates | Validate willingness to pay, improve product |
| Scale (Year 3+) | Annual price increases (5-10%) | Inflation + value increase |

**Grandfathering policy**: Customers on introductory pricing keep their rate for 12 months after general availability.

---

## 7. Competitive Pricing Analysis

| Competitor | Entry Point | Mid-Market | Enterprise | Per-Query Cost |
|------------|-------------|------------|------------|----------------|
| Snowflake Cortex | Included | $2K-10K/mo (compute) | $10K-100K+/mo | High (compute-based) |
| Databricks Genie | Included | $1K-5K/mo (DBUs) | $5K-50K+/mo | High (compute-based) |
| Vanna AI | Free (OSS) | $50/user/mo | Custom | Low |
| WrenAI | Free (OSS) | $99/user/mo | Custom | Low-Medium |
| Seek AI | N/A | N/A | $50K+/yr | Medium |
| ThoughtSpot | N/A | N/A | $100K+/yr | Very High |
| **Our Platform** | **Free** | **$50-150/seat/mo** | **$25K+/yr** | **Low ($0.006/query avg)** |

**Our price positioning**: Below ThoughtSpot and Seek AI for enterprise, competitive with Vanna/WrenAI for mid-market, but with a complete product (not library/framework).

---

## 8. Key Pricing Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Free tier too generous → high hosting costs | Cost > conversion benefit | Set query limits conservatively initially, adjust with data |
| Usage pricing hard to predict for customers | Churn from bill shock | Caps + alerts + annual commits with predictable costs |
| Competitive price pressure | Margin compression | Differentiate on value (accuracy, autonomy), not price |
| Enterprise negotiation pushes price too low | ACV below target | Minimum annual commit for enterprise tier ($25K) |
| Self-hosted pricing too complex | Sales friction | Simple: 2 options (standard + premium support) |

---

## 9. References

| Source | Relevance |
|--------|-----------|
| [Business-Model.md](./Business-Model.md) | Unit economics and revenue projections |
| [Competitor-Analysis.md](./Competitor-Analysis.md) | Competitive pricing comparison |
| [Market-Analysis.md](./Market-Analysis.md) | Customer willingness to pay analysis |
| Stripe "Usage-based pricing for SaaS" (2025) | Best practices for usage pricing |
| DealHub "Enterprise SaaS Pricing" (2026) | Enterprise pricing models |
| m3ter "Enterprise SaaS Pricing Models" (2026) | Consumption-based billing strategies |
