# -*- coding: utf-8 -*-
"""
Implements CephCI logging interface.

In this module, we implement a singleton LOG object that can be used by all components
of CephCI. It supports the below logging methods

    - error
    - warning
    - info
    - debug

Along with the above, it provides support for pushing events to

    - local file
    - logstash server
"""
import logging
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

import logstash

from .config import CephCIConfig
from .utils import Singleton

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"


class LoggerInitializationException:
    pass


class Log(metaclass=Singleton):
    """CephCI Logger object to help streamline logging."""

    def __init__(self) -> None:
        """
        Initializes the logging mechanism based on the inputs provided."""
        self._logger = logging.getLogger()
        self._log_level = logging.INFO
        self._log_dir = None

        self.log_format = LOG_FORMAT

    @property
    def log_dir(self) -> str:
        """Return the absolute path to the logging folder."""
        return self._log_dir

    @property
    def log_level(self) -> int:
        """Return the logging level."""
        return self._log_level

    @property
    def config(self) -> Dict:
        """Return the CephCI run configuration."""
        return CephCIConfig()

    @property
    def run_id(self) -> str:
        """Return the unique identifier of the execution run."""
        return self.config["run_id"]

    @property
    def metadata(self) -> Dict:
        """Return the metadata of the execution run."""
        return dict(
            {
                "test_run_id": self.run_id,
                "testing_tool": "cephci",
                "rhcs": self.config.get("rhcs"),
                "test_build": self.config.get("build", "released"),
            }
        )

    def close(self) -> None:
        """Close all log handlers."""
        handlers = self._logger.handlers[:]
        for handler in handlers:
            handler.close()
            self._logger.removeHandler(handler)

    def _add_logstash_handler(self) -> None:
        """Add Logstash handler."""
        host = self.config["logstash"]["host"]
        port = self.config["logstash"]["port"]
        version = self.config["logstash"].get("version", 1)
        handler = logstash.TCPLogstashHandler(
            host=host,
            port=port,
            version=version,
        )
        handler.setLevel(self.log_level)
        self._logger.addHandler(handler)

        server = f"tcp://{host}:{port}"
        self._logger.debug(f"Log events are also pushed to {server}")

    def create_root_folder(self) -> None:
        """
        Create the logging folder based on the configuration provided by the user.

        Returns:
            None

        Raises:
            LoggerInitializationException.
        """
        if self.config.get("log", {}).get("verbose"):
            self._logger.setLevel(logging.DEBUG)
            self._log_level = logging.DEBUG

        root_log_dir = Path("/ceph/cephci-jenkins")

        if not root_log_dir.exists():
            if self.config.get("log", {}).get("path"):
                root_log_dir = Path(self.config["log"]["path"])
            else:
                root_log_dir = Path("/tmp")

        try:
            log_dir = Path(f"{root_log_dir}/cephci-run-{self.run_id}")
            log_dir.mkdir(exist_ok=True)

            self._log_dir = str(log_dir)

            if self.config.get("logstash"):
                self._add_logstash_handler()

            return
        except FileExistsError:
            self._logger.error("Unable to create log directory.")

        raise LoggerInitializationException

    def add_file_handler(self, log_file: str) -> None:
        """
        Adds a file handler to the logging mechanism.

        Only one file handler is enabled at a time.

        Args:
            log_file (str):     Name to be given to the log file.

        Returns:
            None
        """
        self.close_file_handler()
        _log_file = Path(f"{self.log_dir}/{log_file}").absolute()
        _formatter = logging.Formatter(LOG_FORMAT)

        _file_handler = logging.FileHandler(str(_log_file))
        _file_handler.setFormatter(_formatter)
        _file_handler.setLevel(self.log_level)

        self._logger.addHandler(_file_handler)
        self.debug(f"Log events are also pushed to {_log_file}")

    def close_file_handler(self):
        """Close any file handler associated with the logger."""
        handlers = self._logger.handlers[:]
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self._logger.removeHandler(handler)

    def _log(
        self, level: str, message: Any, metadata: Optional[Dict] = None, **kwargs
    ) -> None:
        """
        Log the given message using the provided level along with the metadata.

        Args:
            level (str):        Log level
            message (Any):      The message that needs to be logged
            metadata (dict):    Extra information to be appended.

        Returns:
            None.
        """
        log = {
            "info": self._logger.info,
            "debug": self._logger.debug,
            "warning": self._logger.warning,
            "error": self._logger.error,
            "exception": self._logger.exception,
        }
        extra = None
        if self.config.get("logstash"):
            extra = deepcopy(self.metadata)
            if metadata:
                extra.update(metadata)

        log[level](message, extra=extra, **kwargs)

    def info(self, message: Any, metadata: Optional[Dict] = None) -> None:
        """
        Log with info level the provided message and extra data.

        Args:
            message (Any):      The message to be logged.
            metadata (dict):    The metadata that would be sent along with the message.

        Returns:
            None
        """
        self._log("info", message, metadata)

    def debug(self, message: Any, metadata: Optional[Dict] = None, **kwargs) -> None:
        """
        Log with debug level the provided message and extra data.

        Args:
            message (str):      The message to be logged.
            metadata (dict):    The metadata that would be sent along with the message.
            kwargs (Any):       Support keyword arguments by logging
        Returns:
            None
        """
        self._log("debug", message, metadata, **kwargs)

    def warning(self, message: Any, metadata: Optional[Dict] = None, **kwargs) -> None:
        """
        Log with warning level the provided message and extra data.

        Args:
            message (Any):      The message to be logged.
            metadata (dict):    The metadata that would be sent along with the message.
            kwargs (Any):       Support keyword arguments by logging
        Returns:
            None
        """
        self._log("warning", message, metadata, **kwargs)

    def error(
            self,
            message: Any,
            metadata: Optional[Dict] = None,
            exc_info: bool = True,
            **kwargs
    ) -> None:
        """
        Log with error level the provided message and extra data.

        Args:
            message (Any):      The message to be logged.
            metadata (dict):    The metadata that would be sent along with the message.
            exc_info (boo):     Exception details to be logged.
            kwargs (Any):       Support keyword arguments by logging
        Returns:
            None
        """
        kwargs["exc_info"] = exc_info
        self._log("error", message, metadata, **kwargs)

    def exception(self, message: Any, exc_info: bool = True, **kwargs) -> None:
        """
        Log the given message under exception log level.

        Args:
            message (Any):  Message or record to be emitted.
            exc_info (boo):     Exception details to be logged.
            kwargs (Any):       Support keyword arguments by logging
        Returns:
            None
        """
        kwargs["exc_info"] = exc_info
        self._log("exception", message, **kwargs)
