from __future__ import annotations

from typing import Any

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import Sampler, TraceIdRatioBased

from app.core.config import get_settings

_tracer: trace.Tracer | None = None
_provider: TracerProvider | None = None


def setup_telemetry(app: Any, service_name: str = "ke-api") -> None:
    global _tracer, _provider

    settings = get_settings()

    resource = Resource.create({
        "service.name": service_name,
        "service.version": settings.app_version,
        "deployment.environment": settings.environment,
    })

    _provider = TracerProvider(
        resource=resource,
        sampler=_build_sampler(settings),
    )

    _try_add_otlp_exporter(settings)
    _provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(_provider)
    _tracer = trace.get_tracer(service_name)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=_provider)


def _build_sampler(settings: Any) -> Sampler:
    if settings.environment == "development":
        from opentelemetry.sdk.trace.sampling import ALWAYS_ON
        return ALWAYS_ON
    from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
    return ALWAYS_OFF


def _try_add_otlp_exporter(settings: Any) -> None:
    endpoint = settings.otel_endpoint
    if not endpoint or endpoint == "http://localhost:4318":
        return
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        _provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
        )
    except ImportError:
        pass


def shutdown_telemetry() -> None:
    global _provider
    if _provider is not None:
        _provider.shutdown()


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("ke-api")
    return _tracer
