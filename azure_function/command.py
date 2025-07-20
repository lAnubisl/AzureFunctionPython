from logging import Logger
import requests

class Command:
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def execute(self) -> None:
        google_resp = requests.get(url='https://google.com', timeout=10)
        self.__logger.info(f"google response status code {google_resp.status_code}")
        msft_resp = requests.get(url='https://www.microsoft.com', timeout=10)
        self.__logger.info(f"msft response status code {msft_resp.status_code}")
