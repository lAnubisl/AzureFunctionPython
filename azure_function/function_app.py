
import logging
import requests
import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.context.context import Context
from opentelemetry.propagate import extract

configure_azure_monitor()
tracer: trace.Tracer = trace.get_tracer(__name__)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest, context) -> None:
    ctx: Context = extract({
      "traceparent": context.trace_context.Traceparent,
      "tracestate": context.trace_context.Tracestate,
    })
    logging.info("Call: TimerTrigger Started")
    await RunBusinessLogic(ctx)
    logging.info("Call: TimerTrigger Ended")

@app.function_name(name="GetRecord")
@app.route(route="GetRecord", methods=["GET"])
async def GetRecord(req: func.HttpRequest, context) -> func.HttpResponse:
    ctx: Context = extract({
      "traceparent": context.trace_context.Traceparent,
      "tracestate": context.trace_context.Tracestate,
    })
    logging.info("Call: GetRecord Started")
    await RunBusinessLogic(ctx)
    logging.info("Call: GetRecord Ended")
    return func.HttpResponse("Done", status_code=200)

async def RunBusinessLogic(ctx: Context) -> None:
    with tracer.start_as_current_span("My Business Logic", context=ctx):
        with tracer.start_as_current_span("HTTP Request to Google", context=ctx):
            google_resp = requests.get(url='https://google.com')
            logging.info(f"google response status code {google_resp.status_code}")
        with tracer.start_as_current_span("HTTP Request to Microsoft", context=ctx):
            msft_resp = requests.get(url='https://www.microsoft.com')
            logging.info(f"msft response status code {msft_resp.status_code}")
