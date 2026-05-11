"""
OpenTelemetry Tracing Setup (R12)

Configures distributed tracing with OpenTelemetry and exports
traces to Grafana Tempo via OTLP gRPC.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.config import get_settings

settings = get_settings()


def setup_tracing(app):
    """Initialize OpenTelemetry tracing for the FastAPI app."""
    resource = Resource.create({
        "service.name": settings.SERVICE_NAME,
        "service.version": "1.0.0",
        "deployment.environment": settings.APP_ENV,
    })

    provider = TracerProvider(resource=resource)

    # Export to Tempo via OTLP
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://tempo:4317",
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    return provider
