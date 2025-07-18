import logging
from command import Command

class DependenciesBuilder:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger("MyApp")

    def get_command(self):
        return Command(self.logger, self.tracer)

    def get_logger(self) -> logging.Logger:
        return self.logger
