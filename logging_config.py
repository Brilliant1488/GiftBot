from loguru import logger

# Конфигурация логирования
logger.add(
    "bot.log",
    rotation="1 MB",
    level="INFO",
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Пример использования:
# logger.debug("Это отладочное сообщение")
# logger.info("Это стандартное сообщение")
# logger.warning("Это предупреждение")
# logger.error("Это ошибка")
