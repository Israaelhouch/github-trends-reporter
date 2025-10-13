import logging
import os
from datetime import datetime

def setup_logger(name: str = "auto_notifier", log_dir: str = "logs"):
    """
    Creates and configures a logger.
    Each run creates a new log file (e.g., logs/run_2025_10_09.log)
    """
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"run_{datetime.utcnow().strftime('%Y_%m_%d')}.log")

    # Configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s | %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
