import logging
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer")
async def timer_trigger(timer: func.TimerRequest) -> None:
    logging.info("Timer trigger function executed")