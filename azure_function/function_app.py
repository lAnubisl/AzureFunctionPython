import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor # type: ignore
from opentelemetry import trace
from dependencies_builder import DependenciesBuilder
from utils import transform_context
from ambient_context_manager import set_context, unset_context, get_context

configure_azure_monitor(
    logger_name="MyApp",
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest, context: func.Context) -> None:
    depencencies_builder = DependenciesBuilder()
    tracer: trace.Tracer = depencencies_builder.get_tracer()
    set_context(transform_context(context))
    try:
        with tracer.start_as_current_span("Execute command", context=get_context()):
            await depencencies_builder.get_command().execute()
    finally:
        unset_context()

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def GetRecord(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    depencencies_builder = DependenciesBuilder()
    tracer: trace.Tracer = depencencies_builder.get_tracer()
    set_context(transform_context(context))
        with tracer.start_as_current_span("Execute command", context=get_context()):
            await depencencies_builder.get_command().execute()
        return func.HttpResponse("Done", status_code=200)
    finally:
        unset_context()
