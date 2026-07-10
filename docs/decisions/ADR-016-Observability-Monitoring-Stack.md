# ADR-016: Observability and Monitoring Stack

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-016 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform comprises 10+ microservices, 3 storage systems (PostgreSQL, Qdrant, Redis), GPU inference endpoints, multi-tenant isolation, and 5 deployment modes. Teams must detect, diagnose, and resolve issues across this distributed system. Observability must cover metrics (RED: Rate, Errors, Duration), logging (structured, searchable), tracing (distributed request context), and alerting (SLO-based burn rate). The solution must be self-hostable for air-gapped deployments while optionally integrating with managed cloud services.

## Decision

Use the open-source CNCF observability stack:

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics collector | Prometheus 2.50+ | Time-series metrics with pull model |
| Metrics visualization | Grafana 11+ | Dashboards, alerting, unified UI |
| Log aggregation | Loki 3.0+ | Log storage without index overhead |
| Distributed tracing | Tempo 2.5+ | Trace storage with OTel-compatible ingestion |
| Instrumentation | OpenTelemetry 1.30+ | Unified SDK for metrics, logs, traces |
| Alerting | Grafana Alerting + Alertmanager | SLO burn rate alerts, notification routing |
| Cost attribution | OpenCost | Multi-tenant Kubernetes cost allocation |

## Rationale

- **Prometheus**: CNCF graduated standard; pull model avoids agent deployment complexity; service discovery via K8s annotations; efficient TSDB with 1:1 compression ratio
- **Grafana**: Single pane for all observability data — Prometheus (metrics), Loki (logs), Tempo (traces), plus cloud provider metrics via plugins
- **Loki**: Log aggregation without Elasticsearch-level indexing overhead — cost-effective at high log volume; Prometheus-style label-based querying; native Grafana integration
- **Tempo**: Trace storage with no sampling or indexing decisions at ingestion time — store everything, query when needed; OTel-native ingestion
- **OpenTelemetry**: Industry standard for instrumentation; vendor-neutral; single SDK emits metrics, logs, and traces with consistent context propagation
- **Self-hosted**: All components are self-hostable — same stack in cloud SaaS, dedicated, VPC, on-prem, and air-gapped. Grafana Cloud available as optional managed alternative for smaller deployments

## Consequences

### Positive
- Single instrumentation standard (OTel) across Python + TypeScript + Go + K8s
- Unified query experience (Grafana Explore: PromQL → LogQL → TraceQL in one interface)
- Cost-effective log storage at scale (Loki is 30-60% cheaper than Elasticsearch for equivalent volume)
- SLO-based alerting reduces alert fatigue compared to threshold-based alerting
- Tempo stores all traces at ingestion time — no sampling decisions to reconfigure
- All components are self-hostable — works identically in all 5 deployment modes

### Negative
- Prometheus pull model does not work in air-gapped environments without ingress configuration
- Loki query performance degrades for complex regex queries across large time ranges vs Elasticsearch
- OTel collector adds operational overhead (must deploy, configure, scale the collector)
- Grafana Alerting is less mature than Alertmanager for complex routing (though improving)
- Self-hosting the observability stack requires significant infrastructure (compute + storage for metrics/logs/traces)
- Tempo's "store everything" approach requires careful storage capacity planning for high-traffic deployments

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Datadog | Cost-prohibitive at scale ($15-23/host/month + $0.10/GB log ingestion); data residency compliance issues for regulated industries |
| New Relic | Similar cost concerns; less flexible querying than PromQL |
| ELK Stack (Elasticsearch, Logstash, Kibana) | Elasticsearch indexing makes log storage 2-3x more expensive than Loki; heavier infrastructure footprint |
| Splunk | Prohibitively expensive for multi-terabyte log volumes at enterprise scale |
| Grafana Cloud | Considered for smaller deployments but rejected as primary — cannot air-gap; data residency concerns |
| Sentry only | Application error tracking only — insufficient for infrastructure and business metrics |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OTel collector becomes bottleneck under high throughput | Medium | High | Horizontal scaling of OTel collector; rate limiting at ingestion; backpressure handling |
| Log volume exceeds storage budget | High | Medium | Log retention policies (7d/30d/90d tiers); sampling verbose logs at source |
| Trace sampling bias misses critical error paths | Medium | High | 100% sampling for error traces; 1% for success traces; head-based + tail-based sampling |
| Alert fatigue from poorly tuned burn rate alerts | High | Medium | Multi-window burn rate (fast + slow burn); alert severity tiers; regular review of alerting rules |
| Team lacks operational expertise for self-hosted observability | Medium | Medium | Runbook documentation for each component; Grafana Cloud as managed fallback |

## Trade-offs

- **Self-hosted vs managed observability**: Self-hosted provides deployment flexibility and cost control but requires operational investment. Managed (Grafana Cloud) is viable for <50 tenants but triggers data residency review for regulated customers
- **Loki vs Elasticsearch**: Loki trades query flexibility for cost efficiency. Elasticsearch would enable full-text log search but at 2-3x storage cost. Loki chosen for the cost-sensitive multi-tenant SaaS model
- **Traces: store everything vs sample at ingestion**: Tempo stores everything at ingestion time (no sampling decision to make) but requires more storage. Balanced by retention-tiered storage (hot/warm/cold)
- **RED vs USE metrics**: RED (Rate, Errors, Duration) for service-level monitoring; USE (Utilization, Saturation, Errors) for infrastructure-level. Both are used — RED for application, USE for infrastructure
- **SLO alerting vs threshold alerting**: SLO burn rate alerts provide earlier warning with less noise but require team understanding of SLO math. Threshold alerts are simpler but generate more noise

## Related ADRs

- ADR-005: Self-Hosted Knowledge Stores Only (self-hosted observability aligns with deployment-agnostic principle)
- ADR-009: Self-Hosted Inference Primary, Cloud Fallback (GPU inference monitoring within observability stack)
- ADR-012: Configuration Management Approach (OTel collector config, Grafana datasource config)
- ADR-015: GPU Vendor Strategy (AMD ROCm telemetry, GPU metrics)

## References

- [Observability-Specification.md](../specifications/Observability-Specification.md) (full specification — 32 SLIs, 6 SLOs, 220+ metrics, 15 critical alerts, 4 playbooks)
- [Deployment-Specification.md](../specifications/Deployment-Specification.md) §16 (Monitoring Integration)
- [Infrastructure-Specification.md](../specifications/Infrastructure-Specification.md) §6 (Observability Infrastructure)
- [Performance-Specification.md](../specifications/Performance-Specification.md) §6 (Observability Requirements)
