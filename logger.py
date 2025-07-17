# Requires loguru. If you see an import error for loguru, install with: pip install loguru
from loguru import logger
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENV = os.getenv("ENVIRONMENT", "development")

logger.remove()
logger.add(
    "logs/error.log",
    level="ERROR",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)
logger.add(
    "logs/info.log",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    enqueue=True
)
if ENV == "development":
    logger.add(lambda msg: print(msg, end=""), level=LOG_LEVEL) 