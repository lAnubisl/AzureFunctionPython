import logging.config
import logging.handlers
import requests
import azure.functions as func
from datetime import datetime, timezone
from azure_storage_table_helper import Record
from azure_storage_table_helper import AzureTableStorageHelper
from opencensus.extension.azure.functions import OpenCensusExtension
from opencensus.trace import config_integration

# https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#log-custom-telemetry
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/asp-net-dependencies#dependency-auto-collection
# https://learn.microsoft.com/en-us/azure/azure-monitor/app/api-custom-events-metrics#trackdependency

config_integration.trace_integrations(['requests'])
OpenCensusExtension.configure()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="Health")
@app.route(route="Health", methods=["GET"])
def Health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)

@app.function_name(name="SetRecord")
@app.route(route="SetRecord", methods=["GET"])
async def CreateRecord(req: func.HttpRequest, context) -> func.HttpResponse:
    logging.info("Info CreateRecord")
    logging.debug("Debug CreateRecord")
    logging.error("Error CreateRecord")
    logging.warning("Warning CreateRecord")
    logging.critical("Critical CreateRecord")
    record: Record = Record(
        "123", "This is a note", 1, True, datetime.now(timezone.utc)
    )
    table_helper = AzureTableStorageHelper()
    with context.tracer.span("TableHelper"):
        await table_helper.set_record(record)
    with context.tracer.span("google"):
        response = requests.get(url='https://google.com')
        logging.info(response.text)
    return func.HttpResponse("Record Created", status_code=200)


@app.function_name(name="GetRecord")
@app.route(route="Record", methods=["GET"])
async def GetRecord(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Info GetRecord")
    logging.debug("Debug GetRecord")
    logging.error("Error GetRecord")
    logging.warning("Warning GetRecord")
    logging.critical("Critical GetRecord")
    table_helper = AzureTableStorageHelper()
    record = await table_helper.get_record("123")
    if record is None:
        return func.HttpResponse("Record Not Found", status_code=404)
    return func.HttpResponse(record.note, status_code=200)
