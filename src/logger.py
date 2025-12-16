import logging
import sys


def setup_logger(name: str = "neuro_chess", level: int = logging.INFO):
    """
    Настраивает логгер с красивым форматированием.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Если хендлеры уже есть (например, при релоаде uvicorn), не добавляем новые
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)

    # Формат: [TIME] [LEVEL] [LOGGER_NAME] Message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Создаем глобальный инстанс для удобного импорта
logger = setup_logger()
