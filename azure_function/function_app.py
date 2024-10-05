import logging.config
import logging.handlers
from datetime import datetime, timezone
import requests
import azure.functions as func

import opentelemetry.trace
from azure.monitor.opentelemetry import configure_azure_monitor

from azure_storage_table_helper import Record
from azure_storage_table_helper import AzureTableStorageHelper
from logger_interface import LoggerInterface
from logger import Logger


# Dependency auto collection does not work for Python
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/asp-net-dependencies#dependency-auto-collection

# There are no examples of how to manually track dependencies for python
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/api-custom-events-metrics#trackdependency

# Enable Application Insights Configuration as described in 'Log custom telemetry':
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#log-custom-telemetry

# https://pypi.org/project/opencensus-extension-azure-functions/

# https://learn.microsoft.com/en-us/azure/architecture/guide/devops/monitor-with-opencensus-application-insights
# https://github.com/Azure/observable-python-azure-functions/blob/initial-branch-code/QueryStep/__init__.py

configure_azure_monitor()
tracer: opentelemetry.trace.Tracer = opentelemetry.trace.get_tracer(__name__)

logger: LoggerInterface = Logger()
tableStorageHelper = AzureTableStorageHelper(logger)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest) -> None:
    logger.info("Call: TimerTrigger")
    with tracer.start_span("HTTP Request to Google"):
        response = requests.get(url='https://google.com')
    logging.info(response.text)

@app.function_name(name="Health")
@app.route(route="Health", methods=["GET"])
def Health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)

@app.function_name(name="SetRecord")
@app.route(route="SetRecord", methods=["GET"])
async def CreateRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Call: CreateRecord")
    record: Record = Record(
        "123", "This is a note", 1, True, datetime.now(timezone.utc)
    )
    with tracer.start_span("Azure Table Storage"):
        await tableStorageHelper.set_record(record)

    with tracer.start_span("HTTP Request to Google"):
        response = requests.get(url='https://google.com')
        logging.info(f"Response code {response.status_code}")
    return func.HttpResponse("Record Created", status_code=200)

@app.function_name(name="GetRecord")
@app.route(route="Record", methods=["GET"])
async def GetRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Call: GetRecord")
    record: Record | None = await tableStorageHelper.get_record("123")
    if record is None:
        return func.HttpResponse("Record Not Found", status_code=404)
    return func.HttpResponse(record.note, status_code=200)
