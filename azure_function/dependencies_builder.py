import logging
from opentelemetry import trace
from command import Command

class DependenciesBuilder:
    def __init__(self):
        self.__logger: logging.Logger = logging.getLogger("MyFunctionApp")
        self.__tracer: trace.Tracer = trace.get_tracer("MyFunctionApp")

    def get_command(self):
        return Command(self.__logger, self.__tracer)

    def get_logger(self) -> logging.Logger:
        return self.__logger
