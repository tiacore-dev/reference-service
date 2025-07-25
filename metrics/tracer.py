import platform

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracer(app):
    resource = Resource(
        attributes={
            "service.name": "reference-fastapi",
            "host.name": platform.node(),
            "deployment.environment": "dev",
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces"))
    tracer_provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app)
