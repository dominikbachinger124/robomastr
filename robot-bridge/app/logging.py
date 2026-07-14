"""Structured logging utilities for the robot bridge."""

import json
import logging
import sys
from typing import Any, MutableMapping


class _JsonFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        output: MutableMapping[str, Any] = {
            "level": record.levelname,
            "time": self.formatTime(record),
            "logger": record.name,
            "event": record.funcName,
            "message": message,
        }
        for key, value in getattr(record, "extra", {}).items():
            if key not in output:
                output[key] = value
        return json.dumps(output, default=str)


class _StructuredLogger:
    """Wrap a standard logger so keyword arguments are stored as extra fields."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._logger.debug(msg, extra={"extra": kwargs})

    def info(self, msg: str, **kwargs: Any) -> None:
        self._logger.info(msg, extra={"extra": kwargs})

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._logger.warning(msg, extra={"extra": kwargs})

    def error(self, msg: str, **kwargs: Any) -> None:
        self._logger.error(msg, extra={"extra": kwargs})

    def exception(self, msg: str, **kwargs: Any) -> None:
        self._logger.exception(msg, extra={"extra": kwargs})


def get_logger(name: str) -> _StructuredLogger:
    """Return a structured logger for the given module name.

    Use this when you need observability inside the robot bridge.
    Do NOT use print() in production code.

    Args:
        name: Typically __name__.

    Returns:
        A structured logger wrapper.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return _StructuredLogger(logger)
