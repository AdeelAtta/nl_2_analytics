# Business Model

**Enterprise Data Intelligence Platform — Phase 1 Product & Business**

| Metadata | Value |
|----------|-------|
| **Author** | Founding CTO |
| **Date** | July 2026 |
| **Status** | Draft |
| **Version** | 1.0 |
| **Cross-References** | [Pricing.md](./Pricing.md), [Market-Analysis.md](./Market-Analysis.md), [USP.md](./USP.md), [Goals.md](./Goals.md) |

---

## 1. Executive Summary

Our business model is a **hybrid usage-based + seat-based SaaS** model targeting mid-market and enterprise customers. Revenue is generated through:

| Revenue Stream | % of Revenue (Year 3) | Margins |
|----------------|----------------------|---------|
| SaaS subscriptions (seat + usage) | 70% | 80%+ |
| Self-hosted enterprise licenses | 20% | 90%+ |
| Professional services (onboarding, training) | 10% | 40% |
| Future: Marketplace, premium integrations | <5% | 90%+ |

**Key metric**: Average Revenue Per Customer (ARPC) targets $25K/year by Year 3, with a path to $100K+ for enterprise.

---

## 2. Revenue Model Detail

### 2.1 SaaS Subscription (Primary)

**Structure**: Base seat fee + usage allowance + overage

| Tier | Seats | Queries/Month | Price | Target Customer |
|------|-------|---------------|-------|-----------------|
| Free | 3 | 100 | $0 | Evaluation, individuals |
| Starter | 10 | 2,000 | $50/seat/mo | Small teams |
| Pro | 25 | 25,000 | $150/seat/mo | Mid-market |
| Enterprise | Unlimited | Custom | Custom | Large enterprise |

**Usage pricing rationale**:
- Seat fee covers: context layer, schema intelligence, governance
- Usage component covers: inference costs, database execution time
- This aligns our costs with customer value — more queries = more value = more revenue

**Hypothesis**: Mid-market customers tolerate $50-150/seat/month for a tool that saves each analyst 15+ hours/week. At $150/seat/month, the tool pays for itself if it saves 2+ hours of analyst time per week.

### 2.2 Self-Hosted / Enterprise License

For enterprises that require on-premises or VPC deployment:

| Component | Pricing |
|-----------|---------|
| Annual license fee | $50K-$500K (based on data volume + users) |
| Support | 20% of license fee annually |
| Professional services | $300-500/hour or fixed-price packages |

**Rationale**: Enterprise self-hosted reduces our hosting costs but increases support costs. License fee must cover the support investment while remaining attractive vs cloud.

### 2.3 Professional Services

| Service | Price | Duration |
|---------|-------|----------|
| Standard onboarding | $5K fixed | 2 days |
| Advanced setup (multi-DB, custom integration) | $15K-$50K | 1-2 weeks |
| Custom schema training | $300/hr | As needed |
| Security review support | $5K fixed | 1 week |

### 2.4 Future Revenue Streams

| Stream | Description | Timeline |
|--------|-------------|----------|
| **Marketplace** | Third-party connectors, semantic models, visualization templates | Phase 3 (2028) |
| **Premium integrations** | Certified connectors for SAP, Oracle EBS, Salesforce | Phase 2 (2027) |
| **Embedded API** | White-label NL2SQL for SaaS platforms | Phase 3 (2028) |
| **Data quality monitoring** | Additional module for anomaly detection | Phase 3 (2028) |
| **AI agent credits** | Per-call pricing for agentic workflows | Phase 3 (2028) |

---

## 3. Unit Economics

### 3.1 Cost per Query

| Component | Simple Query | Medium Query | Complex Query |
|-----------|-------------|--------------|---------------|
| Inference (self-hosted) | $0.0003 | $0.002 | $0.01 |
| Inference (cloud fallback) | — | — | $0.02 |
| Vector retrieval | $0.0001 | $0.0001 | $0.0002 |
| Database execution | $0.001 | $0.005 | $0.02 |
| Total (self-hosted) | **$0.0014** | **$0.0071** | **$0.0302** |
| Total (cloud fallback) | | | **$0.0402** |

**Assumptions**:
- Simple: 65% of queries → SQLCoder-7b (self-hosted)
- Medium: 25% of queries → Qwen2.5-72B (self-hosted)
- Complex: 8% of queries → DeepSeek-V3 (self-hosted)
- Edge: 2% of queries → GPT-4o/Claude (cloud API)

**Weighted average cost per query**: ~$0.006 (self-hosted primary)

### 3.2 Revenue per Query (Starter Tier)

- $50/seat/month ÷ 200 queries/seat/month = $0.25/query
- Cost: ~$0.006/query
- **Gross margin**: ~97.6%

### 3.3 Customer Unit Economics

| Metric | Starter | Pro | Enterprise |
|--------|---------|-----|------------|
| ACV (10 seats) | $6K | $18K | $50K-$500K |
| Implementation cost | $500 | $2K | $10K-$50K |
| Annual support cost (hosting) | $500 | $2K | $5K-$50K |
| Gross margin year 1 | 83% | 78% | 70-80% |
| Gross margin year 3 | 90%+ | 88%+ | 85%+ |

### 3.4 Lifetime Value Projections

| Assumption | Value | Source |
|------------|-------|--------|
| Monthly churn (mid-market) | 3-5% | SaaS benchmarks |
| Annual churn (enterprise) | 5-10% | Enterprise SaaS benchmarks |
| Average customer lifetime | 24-36 months (mid-market) | Conservative estimate |
| LTV (Starter, 10 seats) | ~$15K-$22K | Based on $6K ACV |
| LTV (Pro, 10 seats) | ~$45K-$65K | Based on $18K ACV |
| LTV (Enterprise) | $200K-$1.5M | Based on $100K ACV |
| CAC (mid-market PLG) | $500-$2K | Product-led growth, low touch |
| CAC (enterprise sales) | $20K-$50K | Field sales + marketing |
| LTV:CAC (mid-market) | 10:1+ | Target > 5:1 |
| LTV:CAC (enterprise) | 5:1+ | Target > 3:1 |

---

## 4. Cost Structure

### 4.1 Fixed Costs

| Category | Year 1 | Year 2 | Year 3 |
|----------|--------|--------|--------|
| Engineering | $800K (6-8 people) | $2M (15-20 people) | $4M (30-40 people) |
| Cloud infrastructure | $50K | $200K | $500K |
| GPU hardware (amortized) | $60K (2x MI300X) | $120K (4x MI300X) | $240K (8x MI300X) |
| Cloud inference (fallback) | $20K | $80K | $200K |
| G&A | $100K | $200K | $400K |
| Sales & marketing | $100K (founder-led) | $600K (5 reps) | $1.5M (10 reps + marketing) |
| **Total** | **$1.13M** | **$3.2M** | **$6.84M** |

### 4.2 Variable Costs

| Component | Per Query Cost | % of Queries | Weighted Cost |
|-----------|---------------|--------------|---------------|
| Self-hosted inference | $0.001-$0.01 | 98% | ~$0.004 |
| Cloud inference | $0.01-$0.05 | 2% | ~$0.0006 |
| Vector retrieval | $0.0001 | 100% | $0.0001 |
| Database execution | $0.001-$0.02 | 100% | ~$0.003 |
| **Total variable** | | | **~$0.008/query** |

---

## 5. Revenue Projections

### 5.1 Conservative Scenario

| Year | Customers | Avg ACV | ARR | Burn | Headcount |
|------|-----------|---------|-----|------|-----------|
| 1 (MVP) | 15 | $15K | $225K | $1.13M | 6-8 |
| 2 | 75 | $22K | $1.65M | $3.2M | 20 |
| 3 | 200 | $30K | $6M | $6.84M | 40 |
| 4 | 500 | $40K | $20M | $12M | 70 |
| 5 | 1,200 | $50K | $60M | $20M | 120 |

### 5.2 Base Scenario

| Year | Customers | Avg ACV | ARR | Burn |
|------|-----------|---------|-----|------|
| 1 | 25 | $18K | $450K | $1.13M |
| 2 | 150 | $25K | $3.75M | $3.2M |
| 3 | 500 | $35K | $17.5M | $6.84M |
| 4 | 1,200 | $45K | $54M | $12M |
| 5 | 2,500 | $55K | $137.5M | $20M |

### 5.3 Key Assumptions

| Assumption | Conservative | Base | Aggressive |
|------------|-------------|------|------------|
| Free → paid conversion | 2% | 5% | 8% |
| Net revenue retention | 110% | 120% | 140% |
| Monthly churn (mid-market) | 5% | 4% | 3% |
| Enterprise ACV growth | 20% YoY | 30% YoY | 40% YoY |
| Time to $10M ARR | 48 months | 36 months | 30 months |

---

## 6. Funding Strategy

### 6.1 Capital Requirements

| Round | Amount | Timeline | Use of Funds |
|-------|--------|----------|-------------|
| Pre-seed | $500K-$1M | Now | 4-6 months runway, prototype build |
| Seed | $3M-$5M | Q1 2027 | 12-18 months, MVP launch, first 20 customers |
| Series A | $10M-$15M | Q4 2027-Q1 2028 | 18 months, growth team, scale to 200+ customers |
| Series B | $25M-$40M | 2029 | Market expansion, enterprise sales, industry verticals |

### 6.2 Path to Profitability

| Metric | Year 1 | Year 2 | Year 3 | Year 4 |
|--------|--------|--------|--------|--------|
| ARR | $450K | $3.75M | $17.5M | $54M |
| Gross margin | 75% | 82% | 87% | 90% |
| Opex | $1.13M | $3.2M | $6.84M | $12M |
| Net income | -$680K | -$1M | +$8.4M | +$36M |
| **Breakeven** | | | **Q3 Year 3** | |

---

## 7. Pricing Philosophy

1. **Value-based, not cost-plus**: Price relative to value delivered (analyst salary savings), not inference costs
2. **Simple, not complex**: Two core tiers + enterprise. No hidden fees, no confusing overage calculations
3. **Self-serve to enterprise**: Free tier for evaluation, self-serve for mid-market, sales-led for enterprise
4. **Predictable for customers**: Annual contracts with known costs; usage-based components capped
5. **Aligns with our costs**: Seat fee covers context layer; usage covers inference (variable costs)

---

## 8. Risks to Business Model

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inference costs don't decrease as expected | Margin compression | Self-hosted primary + tiered routing |
| Churn higher than modeled | Revenue shortfall | Focus on stickiness (context accumulation, integrations) |
| Enterprise sales cycle depletes runway | Burn rate > revenue | PLG generates cash while enterprise builds |
| Free tier costs exceed conversion benefit | Unit economics | Tight usage limits on free tier |
| Competitors race to zero on pricing | Price pressure | Differentiate on value (autonomous context), not price |

---

## 9. References

| Source | Relevance |
|--------|-----------|
| [Pricing.md](./Pricing.md) | Detailed pricing tables and rationale |
| [Market-Analysis.md](./Market-Analysis.md) | Market sizing and customer segments |
| [Goals.md](./Goals.md) | Revenue and customer milestones by phase |
| Stripe "Usage-based pricing for SaaS" (2025) | Usage-based pricing best practices |
| DealHub "Enterprise SaaS Pricing" (2026) | Enterprise pricing models |
| m3ter "Enterprise SaaS Pricing Models" (2026) | Consumption-based billing strategies |
| Engineered Insight "Cost Models for NL2SQL Systems" (2026) | NL2SQL-specific cost modeling |
