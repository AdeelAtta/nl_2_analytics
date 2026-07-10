# Agent: Research

| Metadata | Value |
|----------|-------|
| **Agent ID** | AGENT-RESEARCH |
| **Owns Epics** | EP-017 |
| **Workspace** | `/research/` |
| **Reads** | `/docs/Open-Questions.md`, `/docs/epics/EP-017` |

---

## Responsibilities

1. Execute SPIKE-001: Context Layer Accuracy experiment
2. Execute SPIKE-002: Cold-Start Strategy experiment
3. Execute SPIKE-003: Model Router Accuracy experiment
4. Document findings with data-driven recommendations
5. File ADRs if architecture changes are needed based on findings

## Workspace Boundaries

```
/research/
  /context-accuracy/
    experiment.py           -> Experiment harness
    schemas/                -> Sample enterprise schemas
    queries.json            -> Benchmark queries with annotations
    findings.md             -> Results and recommendations
  /cold-start/
    experiment.py           -> Experiment harness
    findings.md             -> Results and recommendations
  /model-router/
    experiment.py           -> Experiment harness
    queries.json            -> Labeled query set
    findings.md             -> Results and recommendations
```

## DO NOT Touch

- `/backend/`
- `/frontend/`
- `/infra/`

## Prompts

### Context Accuracy Experiment Prompt
```
Execute SPIKE-001: Context Layer Accuracy.

Create experiment.py that:
1. Loads 3 enterprise schema samples (100-500 tables each)
2. Loads 50 benchmark queries with annotated relevant schema
3. Implements 3 retrieval strategies:
   a. Vector-only (BGE-M3 dense embeddings)
   b. Hybrid (vector + BM25 keyword)
   c. Hybrid + graph traversal
4. Measures for each: precision@10, recall@10, context window usage
5. Outputs results to findings.md

Success criteria: precision@10 > 0.8 for at least 2/3 schemas.

Document findings in findings.md with:
- Methodology
- Raw results (tables)
- Analysis
- Recommendation
```

## Definition of Done
- All 3 experiments completed
- Findings documented in /research/*/findings.md
- Decision gates triggered if needed (ADRs filed)
- All task status files updated
