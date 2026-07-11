# Competitive Assessment

**Score: 50/100 — PARTIALLY VERIFIED**

---

## 1. Direct Competitors

### Vanna.ai
- **Approach:** RAG over schema information + LLM generation
- **OpenQuery advantage:** 10-layer guardrail stack (Vanna has minimal validation), self-learning loop, multi-DB connectors, multi-tier model routing
- **Vanna advantage:** More mature, larger community, simpler setup, proven accuracy benchmarks
- **Verdict:** OpenQuery has superior architecture but Vanna has execution advantage

### Dataherald
- **Approach:** Enterprise NL2SQL API with fine-tuned models
- **OpenQuery advantage:** Open-source stack, self-learning, broader DB support, hybrid retrieval
- **Dataherald advantage:** Enterprise-ready managed service, SLAs, SOC 2
- **Verdict:** Dataherald is ahead on enterprise readiness; OpenQuery ahead on architecture

### LangChain SQL Agent
- **Approach:** LangChain toolkit for Text-to-SQL
- **OpenQuery advantage:** Purpose-built for SQL (not general-purpose agent), deterministic guardrails, production-hardened, no LangChain dependency
- **LangChain advantage:** Massive ecosystem, flexibility, rapid prototyping
- **Verdict:** OpenQuery is more production-ready; LangChain is more flexible

## 2. Platform Competitors

| Platform | Key Strength | OpenQuery Response |
|----------|-------------|-------------------|
| Snowflake Cortex | Deep integration, managed | Multi-cloud, any DB |
| Databricks AI | Lakehouse, Unity Catalog | Open architecture, no vendor lock-in |
| Microsoft Fabric Copilot | Azure ecosystem, GPT-4 | Multi-cloud, self-learning |
| Google Cloud SQL AI | BigQuery, Vertex AI | Multi-cloud, guardrail stack |

## 3. Competitive Advantage Summary

| Factor | OpenQuery | Competitors |
|--------|-----------|-------------|
| SQL Injection Protection | ✅ 4-layer defense | ❌ Most have none |
| Multi-DB Support | ✅ 5 connectors | ⚠️ 1-2 typically |
| Self-Learning | ✅ Full loop | ❌ Most are static |
| Guardrails | ✅ 10 deterministic layers | ⚠️ 1-2 layers typical |
| Multi-Tier Routing | ✅ 4 tiers with fallback | ⚠️ Single model typically |
| Hybrid Retrieval | ✅ Dense + sparse | ⚠️ Dense-only typically |
| Cold-Start | ❌ Not solved | ❌ Not solved |
| Accuracy Benchmarks | ❌ None | ⚠️ Vanna/Dataherald have some |

**Competitive Verdict: 50/100 — Architecture is genuinely differentiated but unvalidated against competitors. The guardrail stack is the strongest competitive advantage. The lack of accuracy benchmarks is the biggest competitive risk.**
