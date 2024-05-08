import logging


class LoggerConfig:
    _logger: logging.Logger = None

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger('pyschwab')
            cls._logger.setLevel(logging.DEBUG)
            cls._logger.addHandler(logging.NullHandler())
        return cls._logger

logger = LoggerConfig.get_logger()
