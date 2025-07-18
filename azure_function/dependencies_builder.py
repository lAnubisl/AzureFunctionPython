import logging
import opentelemetry
import opentelemetry.trace
from command import Command

class DependenciesBuilder:
    def __init__(self):
        self.tracer: opentelemetry.trace.Tracer = opentelemetry.trace.get_tracer("MyApp")
        self.logger: logging.Logger = logging.getLogger("MyApp")

    def get_command(self):
        return Command(self.logger, self.tracer)

    def get_tracer(self) -> opentelemetry.trace.Tracer:
        return self.tracer

    def get_logger(self) -> logging.Logger:
        return self.logger
