import azure.functions as func
from utils import transform_context
from ambient_context_manager import set_context, unset_context
from azure.monitor.opentelemetry import configure_azure_monitor # type: ignore

configure_azure_monitor(
    logger_name="MyFunctionApp",
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest, context: func.Context) -> None:
    set_context(transform_context(context))
    try:
        from dependencies_builder import DependenciesBuilder
        depencencies_builder = DependenciesBuilder()
        await depencencies_builder.get_command().execute()
    finally:
        unset_context()