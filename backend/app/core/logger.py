"""
Logging configuration using loguru.
"""
import sys
from pathlib import Path
from loguru import logger


# Configure loguru: Remove default handler
logger.remove()

# Get base directory for logs
BASE_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "mdp.log"


# Console output (stderr) with colors for local dev
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{extra[request_id]}</cyan> | <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# File output with rotation and retention
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[request_id]} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,  # Thread-safe logging
)


# Export configured logger
__all__ = ["logger"]

