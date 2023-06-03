import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="Health")
def Health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Healthy", status_code=200)