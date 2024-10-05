import logging
import requests
import azure.functions as func
import opentelemetry.trace
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()
tracer: opentelemetry.trace.Tracer = opentelemetry.trace.get_tracer(__name__)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 * * * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest) -> None:
    logging.info("Call: TimerTrigger Started")
    await RunBusinessLogic()
    logging.info("Call: TimerTrigger Ended")

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def GetRecord(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Call: GetRecord Started")
    await RunBusinessLogic()
    logging.info("Call: GetRecord Ended")
    return func.HttpResponse("Done", status_code=200)

async def RunBusinessLogic() -> None:
    with tracer.start_as_current_span("My Business Logic"):
        with tracer.start_as_current_span("HTTP Request to Google"):
            google_resp = requests.get(url='https://google.com')
            logging.info(f"google response status code {google_resp.status_code}")
        with tracer.start_as_current_span("HTTP Request to Microsoft"):
            msft_resp = requests.get(url='https://www.microsoft.com')
            logging.info(f"msft response status code {msft_resp.status_code}")
