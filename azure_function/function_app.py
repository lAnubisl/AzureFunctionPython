import logging.config
import logging.handlers
import azure.functions as func


logger = logging.getLogger("root")
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="Health")
def Health(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info Health Check")
    logger.debug("Debug Health Check")
    logger.error("Error Health Check")
    logger.warning("Warning Health Check")
    logger.critical("Critical Health Check")
    return func.HttpResponse("Healthy", status_code=200)
