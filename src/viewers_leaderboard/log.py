import sys
from loguru import logger

logger.remove()
logger.add(
    sink=sys.stdout,
    format="{time} | <level>{level}:</level> <cyan>{name: <8}</cyan> | <level>{message}</level>",
    colorize=True,
)
