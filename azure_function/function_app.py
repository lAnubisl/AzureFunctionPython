import logging
import requests
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor # type: ignore
from opentelemetry import trace
from dependencies_builder import DependenciesBuilder

configure_azure_monitor()
depencencies_builder = DependenciesBuilder()
tracer: trace.Tracer = trace.get_tracer(__name__)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest, context: func.Context) -> None:
    depencencies_builder.ambient_context.set_opentelimetry_context(context)
    logging.info("Call: TimerTrigger Started")
    await RunBusinessLogic()
    logging.info("Call: TimerTrigger Ended")

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def GetRecord(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    depencencies_builder.ambient_context.set_opentelimetry_context(context)
    logging.info("Call: GetRecord Started")
    await RunBusinessLogic()
    logging.info("Call: GetRecord Ended")
    return func.HttpResponse("Done", status_code=200)

async def RunBusinessLogic() -> None:
    with tracer.start_as_current_span("My Business Logic", context=depencencies_builder.ambient_context.get_opentelimetry_context()):
        with tracer.start_as_current_span("HTTP Request to Google"):
            google_resp = requests.get(url='https://google.com')
            logging.info(f"google response status code {google_resp.status_code}")
        with tracer.start_as_current_span("HTTP Request to Microsoft"):
            msft_resp = requests.get(url='https://www.microsoft.com')
            logging.info(f"msft response status code {msft_resp.status_code}")
