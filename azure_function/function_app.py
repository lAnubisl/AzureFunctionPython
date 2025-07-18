import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor # type: ignore
from opentelemetry import trace
from dependencies_builder import DependenciesBuilder

configure_azure_monitor()
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest) -> None:
    depencencies_builder = DependenciesBuilder()
    await depencencies_builder.get_command().execute()