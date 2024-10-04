import logging.config
import logging.handlers
from datetime import datetime, timezone
import requests
import azure.functions as func
from opencensus.extension.azure.functions import OpenCensusExtension
from opencensus.trace import config_integration
from azure_storage_table_helper import Record
from azure_storage_table_helper import AzureTableStorageHelper
from logger_interface import LoggerInterface
from logger import Logger

# https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#log-custom-telemetry
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/asp-net-dependencies#dependency-auto-collection
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/api-custom-events-metrics#trackdependency


# Enable Application Insights Configuration as described in 'Log custom telemetry':
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#log-custom-telemetry
config_integration.trace_integrations(['requests']) # type: ignore
OpenCensusExtension.configure() # type: ignore

logger: LoggerInterface = Logger()
tableStorageHelper = AzureTableStorageHelper(logger)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="Health")
@app.route(route="Health", methods=["GET"])
def Health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)

@app.function_name(name="SetRecord")
@app.route(route="SetRecord", methods=["GET"])
async def CreateRecord(req: func.HttpRequest, context) -> func.HttpResponse:
    logger.info("Call: CreateRecord")
    record: Record = Record(
        "123", "This is a note", 1, True, datetime.now(timezone.utc)
    )
    with context.tracer.span("TableHelper"):
        await tableStorageHelper.set_record(record)
    response = requests.get(url='https://google.com')
    logging.info(response.text)
    return func.HttpResponse("Record Created", status_code=200)


@app.function_name(name="GetRecord")
@app.route(route="Record", methods=["GET"])
async def GetRecord(req: func.HttpRequest, context) -> func.HttpResponse:
    logger.info("Call: GetRecord")
    record: Record | None = await tableStorageHelper.get_record("123")
    if record is None:
        return func.HttpResponse("Record Not Found", status_code=404)
    return func.HttpResponse(record.note, status_code=200)
