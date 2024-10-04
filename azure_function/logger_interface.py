import abc

class LoggerInterface(abc.ABC):

    @abc.abstractmethod
    def info(self, message: str):
        """
        Log message with loglevel="Information"
        """
    @abc.abstractmethod
    def debug(self, message: str):
        """
        Log message with loglevel="Debug"
        """
