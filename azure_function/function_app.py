import logging.config
import logging.handlers
import azure.functions as func
from datetime import datetime, timezone
from azure_storage_table_helper import Record
from azure_storage_table_helper import AzureTableStorageHelper
from opencensus.extension.azure.functions import OpenCensusExtension
from opencensus.trace import config_integration

# https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=get-started%2Casgi%2Capplication-level&pivots=python-mode-decorators#log-custom-telemetry


config_integration.trace_integrations(['requests'])
OpenCensusExtension.configure()

logger = logging.getLogger("azure")
logger.setLevel(logging.ERROR)

logger = logging.getLogger("msal")
logger.setLevel(logging.ERROR)

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="Health")
@app.route(route="Health", methods=["GET"])
def Health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)

@app.function_name(name="SetRecord")
@app.route(route="SetRecord", methods=["GET"])
async def CreateRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info CreateRecord")
    logger.debug("Debug CreateRecord")
    logger.error("Error CreateRecord")
    logger.warning("Warning CreateRecord")
    logger.critical("Critical CreateRecord")
    record: Record = Record(
        "123", "This is a note", 1, True, datetime.now(timezone.utc)
    )
    table_helper = AzureTableStorageHelper(logger)
    await table_helper.set_record(record)
    return func.HttpResponse("Record Created", status_code=200)


@app.function_name(name="GetRecord")
@app.route(route="Record", methods=["GET"])
async def GetRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info GetRecord")
    logger.debug("Debug GetRecord")
    logger.error("Error GetRecord")
    logger.warning("Warning GetRecord")
    logger.critical("Critical GetRecord")
    table_helper = AzureTableStorageHelper(logger)
    record = await table_helper.get_record("123")
    if record is None:
        return func.HttpResponse("Record Not Found", status_code=404)
    return func.HttpResponse(record.note, status_code=200)
