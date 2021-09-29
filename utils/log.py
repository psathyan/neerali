"""Provides methods associated with logger."""
import logging
from pathlib import Path


def add_log_file_handler(parent_dir: str, file_name: str, log_level: int) -> None:
    """
    Adds a handler to the logger using the given path and filename.

    Args:
        parent_dir (str)    Name of the directory to be used to store the file
        file_name (str)     Name of the file to be used for storing the logs
        log_level (int)          verbosity level for the logging

    Returns:
        None
    """
    log_dir = create_run_dir(parent_dir)
    log_file = Path(f"{log_dir}/{file_name}").absolute()

    log_handler = logging.FileHandler(str(log_file))
    log_handler.setLevel(log_level)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    log_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.info(f"Logging to file {str(log_file)} is enabled")


def close_and_remove_file_handlers(logger=logging.getLogger()):
    """
    Close FileHandlers and then remove them from the loggers handlers list.

    Args:
        logger: the logger in which to remove the handlers from, defaults to root logger

    Returns:
        None
    """
    handlers = logger.handlers[:]
    for h in handlers:
        if isinstance(h, logging.FileHandler):
            h.close()
            logger.removeHandler(h)
