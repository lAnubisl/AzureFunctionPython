import logging.config
import logging.handlers
import azure.functions as func
from datetime import datetime, timezone
from azure_function.azure_storage_table_helper import Record
from azure_function.azure_storage_table_helper import AzureTableStorageHelper


logger = logging.getLogger("root")
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
table_helper = AzureTableStorageHelper(logger)


@app.route(route="Health")
def Health(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info Health Check")
    logger.debug("Debug Health Check")
    logger.error("Error Health Check")
    logger.warning("Warning Health Check")
    logger.critical("Critical Health Check")
    return func.HttpResponse("Healthy", status_code=200)


@app.route(route="SetRecord", methods=["GET"])
def CreateRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info CreateRecord")
    logger.debug("Debug CreateRecord")
    logger.error("Error CreateRecord")
    logger.warning("Warning CreateRecord")
    logger.critical("Critical CreateRecord")
    record: Record = Record(
        "123", "This is a note", 1, True, datetime.now(timezone.utc)
    )
    table_helper.set_record(record)
    return func.HttpResponse("Record Created", status_code=200)


@app.route(route="Record", methods=["GET"])
async def GetRecord(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info GetRecord")
    logger.debug("Debug GetRecord")
    logger.error("Error GetRecord")
    logger.warning("Warning GetRecord")
    logger.critical("Critical GetRecord")
    record = await table_helper.get_record("123")
    if record is None:
        return func.HttpResponse("Record Not Found", status_code=404)
    return func.HttpResponse(record.note, status_code=200)
