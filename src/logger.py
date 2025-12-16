import logging
import sys

from src.config import LOGGER_DATEFMT, LOGGER_FORMAT, LOGGER_LEVEL, LOGGER_NAME


def setup_logger(name: str = LOGGER_NAME, level: int = LOGGER_LEVEL):
    """
    Configure logger with formatted output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(fmt=LOGGER_FORMAT, datefmt=LOGGER_DATEFMT)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
