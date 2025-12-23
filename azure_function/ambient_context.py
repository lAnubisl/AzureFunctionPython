from contextvars import ContextVar

import azure.functions as func
from opentelemetry.context import Context
from opentelemetry.propagate import extract

class AmbientContext:
    """
    Implements the Ambient Context pattern
    """
    def __init__(self):
        self.__open_telemetry_context = ContextVar(
            "opentelemetry.context",
            default=Context()
        )

    def get_opentelemetry_context(self) -> Context:
        """
        Get the OpenTelemetry context
        """
        return self.__open_telemetry_context.get()

    def set_opentelemetry_context(self, context: func.Context) -> None:
        """
        Set the OpenTelemetry context from the Azure Function context
        Documentation: https://pypi.org/project/azure-monitor-opentelemetry/
        Section: 'Monitoring in Azure Functions'
        """
        ctx: Context = extract({
            "traceparent": context.trace_context.Traceparent, # type: ignore
            "tracestate": context.trace_context.Tracestate, # type: ignore
        }) # type: ignore
        self.__open_telemetry_context.set(ctx)
