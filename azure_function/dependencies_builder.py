import logging
import opentelemetry
import opentelemetry.trace
from command import Command

class DependenciesBuilder:
    def __init__(self):
        self.tracer: opentelemetry.trace.Tracer = opentelemetry.trace.get_tracer(__name__)
        self.logger: logging.Logger = logging.getLogger(__name__)

    def get_command(self):
        return Command(self.logger, self.tracer)
