from logging import Logger
import requests
from opentelemetry.trace import Tracer

class Command:
    def __init__(self, logger: Logger, tracer: Tracer):
        self.__logger = logger
        self.__tracer = tracer

    async def execute(self) -> None:
        with self.__tracer.start_as_current_span("HTTP Request to Google"):
            google_resp = requests.get(url='https://google.com', timeout=10)
            self.__logger.info(f"google response status code {google_resp.status_code}")
        with self.__tracer.start_as_current_span("HTTP Request to Microsoft"):
            msft_resp = requests.get(url='https://www.microsoft.com', timeout=10)
            self.__logger.info(f"msft response status code {msft_resp.status_code}")
