import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger():
    # Define log directory in user's cache
    log_dir = os.path.expanduser("~/.cache/adaptive-cachy-beauty")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Create logger
    logger = logging.getLogger("CachyBeautyEngine")

    # If logger already has handlers, return it to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    # Allow overriding log level via environment variable (e.g. ACB_LOG_LEVEL=DEBUG)
    env_level = os.environ.get("ACB_LOG_LEVEL", "DEBUG").upper()
    log_level = getattr(logging, env_level, logging.DEBUG)
    logger.setLevel(log_level)

    # Console level: mirrors env var, defaults to INFO if not set
    console_level = log_level if log_level <= logging.DEBUG else logging.INFO

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # File Handler (Rotating log file up to 5MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console Handler for real-time terminal viewing
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized. File logging to: {log_file}")
    if env_level != "DEBUG":
        logger.info(f"Log level set to: {env_level} (via ACB_LOG_LEVEL)")

    return logger


# Create a singleton instance
logger = setup_logger()
