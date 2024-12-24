from contextvars import ContextVar
from opentelemetry.propagate import extract
import azure.functions as func
import opentelemetry.context as opentelimetry

class AmbientContext:
    """
    Impelments the Ambient Context pattern
    """
    def __init__(self):
        self.__open_telimetry_context = ContextVar(
            "opentelemetry.context",
            default=opentelimetry.Context())

    def get_opentelimetry_context(self) -> opentelimetry.Context:
        """
        Get the OpenTelemetry context
        """
        return self.__open_telimetry_context.get()

    def set_opentelimetry_context(self, context: func.Context) -> None:
        """
        Set the OpenTelemetry context from the Azure Function context
        Documentation: https://pypi.org/project/azure-monitor-opentelemetry/
        Section: 'Monitoring in Azure Functions'
        """
        ctx: opentelimetry.Context = extract({
            "traceparent": context.trace_context.Traceparent, # type: ignore
            "tracestate": context.trace_context.Tracestate, # type: ignore
        }) # type: ignore
        self.__open_telimetry_context.set(ctx)
