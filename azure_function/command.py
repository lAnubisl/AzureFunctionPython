from logging import Logger
import aiohttp
from opentelemetry.trace import Tracer, SpanKind
from ambient_context_manager import get_context

class Command:
    def __init__(self, logger: Logger, tracer: Tracer):
        self.__logger = logger
        self.__tracer: Tracer = tracer

    def span(self, name: str):
        span = self.__tracer.start_as_current_span(name=name, context=get_context(), kind=SpanKind.CLIENT)
        span.set_attribute("db.system", "MyAPI2")
        return span

    async def execute(self) -> None:
        async with aiohttp.ClientSession() as session:
            with self.span(name="Get Google Page"):
                async with session.get('https://www.google.com') as google_resp:
                    self.__logger.info(f"google response status code {google_resp.status}")

            with self.span(name="Get Microsoft Page"):
                async with session.get('https://www.microsoft.com') as msft_resp:
                    self.__logger.info(f"msft response status code {msft_resp.status}")
