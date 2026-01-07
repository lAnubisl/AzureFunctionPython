import azure.functions as func
from opentelemetry import trace
from dependencies_builder import DependenciesBuilder

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest) -> None:
    builder = DependenciesBuilder()
    tracer: trace.Tracer = builder.get_tracer()
    with tracer.start_as_current_span("Execute command"):
        await builder.get_command().execute()

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def get_record(req: func.HttpRequest) -> func.HttpResponse:
    builder = DependenciesBuilder()
    tracer: trace.Tracer = builder.get_tracer()
    with tracer.start_as_current_span("Execute command"):
        await builder.get_command().execute()
    return func.HttpResponse("Done", status_code=200)
