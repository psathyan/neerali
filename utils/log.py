"""Provides methods associated with logger."""
import logging
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"


def create_or_get_root_log_dir(run_id: str, log_dir: Optional[str] = None) -> str:
    """
    Create the root log directory for storing the log files.

    Args:
        run_id (str):   Unique ID of the test run to be used as root directory
        log_dir (str):  log directory. default: "/tmp"

    Returns:
        Full path of the created directory
    """
    root_log_dir = Path("/ceph/cephci-jenkins")

    if not root_log_dir.exists():
        root_log_dir = log_dir if log_dir else "/tmp"

    log_dir = Path(f"{root_log_dir}/cephci-run-{run_id}")
    try:
        log_dir.mkdir(exist_ok=True)
    except FileExistsError:
        print("Unable to create log directory.")
        raise

    return str(log_dir)


def add_log_file_handler(run_id: str, file_name: str, log_level: int) -> None:
    """
    Adds a handler to the logger using the given path and filename.

    Args:
        run_id (str):       Unique execution identifier
        file_name (str):    Name of the file to be used for storing the logs
        log_level (int):    verbosity level for the logging

    Returns:
        None
    """
    log_dir = create_or_get_root_log_dir(run_id)
    log_file = Path(f"{log_dir}/{file_name}").absolute()
    _formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(str(log_file))
    file_handler.setFormatter(_formatter)
    file_handler.setLevel(log_level)

    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.info(f"Starting to log to {str(log_file)}.")


def close_and_remove_file_handlers(logger=logging.getLogger()):
    """
    Close FileHandlers and then remove them from the loggers handlers list.

    Args:
        logger: the logger in which to remove the handlers from, defaults to root logger

    Returns:
        None
    """
    handlers = logger.handlers[:]
    for handler in handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logger.removeHandler(handler)


def close_log_handlers(logger=logging.getLogger()):
    """
    Close FileHandlers and then remove them from the loggers handlers list.

    Args:
        logger: the logger in which to remove the handlers from, defaults to root logger

    Returns:
        None
    """
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
