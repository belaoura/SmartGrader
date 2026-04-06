"""Logging configuration for SmartGrader."""

import logging
import os


def setup_logging(log_level="INFO", log_file=None):
    """Configure application-wide logging.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        log_file: Path to log file. If None, logs to console only.
    """
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger("smartgrader")
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger
