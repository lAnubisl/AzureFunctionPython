import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor # type: ignore
from opentelemetry import trace
from dependencies_builder import DependenciesBuilder
from utils import transform_context

configure_azure_monitor()
depencencies_builder = DependenciesBuilder()
tracer: trace.Tracer = trace.get_tracer(__name__)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest, context: func.Context) -> None:
    with tracer.start_as_current_span("Execute command", context=transform_context(context)):
        await depencencies_builder.get_command().execute()

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def GetRecord(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    with tracer.start_as_current_span("Execute command", context=transform_context(context)):
        await depencencies_builder.get_command().execute()
    return func.HttpResponse("Done", status_code=200)
