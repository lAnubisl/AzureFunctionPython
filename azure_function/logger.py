import logging
from logger_interface import LoggerInterface

class Logger(LoggerInterface):
    def info(self, message: str):
        logging.info(message)
    def debug(self, message: str):
        logging.debug(message)
