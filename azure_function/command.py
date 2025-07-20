from logging import Logger
import aiohttp

class Command:
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def execute(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.google.com') as google_resp:
                self.__logger.info(f"google response status code {google_resp.status}")
            async with session.get('https://www.microsoft.com') as msft_resp:
                self.__logger.info(f"msft response status code {msft_resp.status}")
