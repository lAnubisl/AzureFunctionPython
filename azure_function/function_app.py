import logging.config
import azure.functions as func
import yaml

with open("log_conf.yaml", "rt") as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger("root")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="Health")
def Health(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Info Health Check")
    logger.debug("Debug Health Check")
    logger.error("Error Health Check")
    logger.warning("Warning Health Check")
    logger.critical("Critical Health")
    return func.HttpResponse("Healthy", status_code=200)
