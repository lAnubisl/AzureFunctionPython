from logging import Logger
import aiohttp
from opentelemetry.trace import Tracer, SpanKind
from ambient_context_manager import get_context

class Command:
    def __init__(self, logger: Logger, tracer: Tracer):
        self.__logger = logger
        self.__tracer: Tracer = tracer

    async def execute(self) -> None:
        async with aiohttp.ClientSession() as session:
            with self.__tracer.start_as_current_span(name="Get Google Page", context=get_context(), kind=SpanKind.SERVER):
                async with session.get('https://www.google.com') as google_resp:
                    self.__logger.info(f"google response status code {google_resp.status}")

            with self.__tracer.start_as_current_span(name="Get Microsoft Page", context=get_context(), kind=SpanKind.SERVER):
                async with session.get('https://www.microsoft.com') as msft_resp:
                    self.__logger.info(f"msft response status code {msft_resp.status}")
