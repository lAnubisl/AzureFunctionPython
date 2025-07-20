from logging import Logger
import aiohttp
from opentelemetry.trace import Tracer, SpanKind, use_span
from ambient_context_manager import get_context

class Command:
    def __init__(self, logger: Logger, tracer: Tracer):
        self.__logger = logger
        self.__tracer: Tracer = tracer

    def span(self, name: str):
        span = self.__tracer.start_span(name=name, context=get_context(), kind=SpanKind.CLIENT)
        span.set_attribute("db.system", "MyAPI2")
        return span

    async def execute(self) -> None:
        async with aiohttp.ClientSession() as session:
            with use_span(self.span(name="Get Google Page"), end_on_exit=True):
                async with session.get('https://www.google.com') as google_resp:
                    self.__logger.info(f"google response status code {google_resp.status}")

            with use_span(self.span(name="Get Microsoft Page"), end_on_exit=True):
                async with session.get('https://www.microsoft.com') as msft_resp:
                    self.__logger.info(f"msft response status code {msft_resp.status}")
