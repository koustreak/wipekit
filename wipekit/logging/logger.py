# wipekit - Enterprise logging module
# Copyright (c) 2025 Wipekit Authors
# MIT License

"""Enterprise-level Logging System for wipekit

This module provides a robust, configurable logging system for enterprise applications. 
Features include:
- Multiple output formats (text, JSON)
- Flexible logging handlers (console, file, rotating file, syslog)
- Log level management per module
- Structured logging support
- Integration with external logging systems
- Performance optimizations for high-throughput environments

Example:
    >>> from wipekit.logging import get_logger, configure_logger, LogLevel, LogFormat
    >>> # Configure global logging settings
    >>> configure_logger(level=LogLevel.INFO, format=LogFormat.JSON, 
    ...                  log_file="app.log", rotation=True)
    >>> # Get a module-specific logger
    >>> logger = get_logger("wipekit.anonymization")
    >>> logger.info("Processing data batch", extra={"batch_id": 12345, "records": 500})
"""

import os
import sys
import json
import logging
import datetime
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Union, List, Callable
from logging.handlers import RotatingFileHandler, SysLogHandler, TimedRotatingFileHandler

# Singleton registry to store loggers
_LOGGERS = {}
# Global configuration
_GLOBAL_CONFIG = {}


class LogLevel(Enum):
    """Standard log levels with clear semantics for enterprise applications."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Available log format styles."""
    TEXT = "text"  # Human-readable text format
    JSON = "json"  # Structured JSON format for machine processing
    COMPACT = "compact"  # Minimalist format for space efficiency


class LogHandler(Enum):
    """Available log handlers."""
    CONSOLE = "console"
    FILE = "file"
    ROTATING_FILE = "rotating_file"
    TIMED_ROTATING_FILE = "timed_rotating_file"
    SYSLOG = "syslog"


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging and machine readability."""

    def __init__(self, include_timestamp: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record):
        log_data = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add timestamp if requested
        if self.include_timestamp:
            log_data["timestamp"] = datetime.datetime.fromtimestamp(
                record.created
            ).isoformat()

        # Add location information
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields from the record
        if hasattr(record, "_extra") and record._extra:
            log_data["data"] = record._extra

        # Add process and thread info for diagnostics
        log_data["process"] = {
            "id": record.process,
            "name": record.processName
        }
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName
        }

        return json.dumps(log_data)


class CompactFormatter(logging.Formatter):
    """Compact log formatter for minimal log size while retaining readability."""

    def __init__(self, include_timestamp: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp

    def format(self, record):
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S") if self.include_timestamp else ""
        prefix = f"{timestamp} {record.levelname[0]} " if timestamp else f"{record.levelname[0]} "

        msg = f"{prefix}{record.name}: {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            exception_msg = traceback.format_exception_only(record.exc_info[0], record.exc_info[1])[0].strip()
            msg += f" | {exception_msg}"

        return msg


class WipekitLogger(logging.Logger):
    """Enhanced logger with additional enterprise features."""

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def _log_with_extra(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """Enhanced logging to handle extra data more gracefully for structured logging."""
        if extra is not None:
            # Store extra in a dedicated attribute to avoid conflicts
            if not isinstance(extra, dict):
                extra = {"data": extra}

        # Call standard logger method with properly processed extra data
        extra_record = {"_extra": extra} if extra else None
        super()._log(level, msg, args, exc_info, extra_record, stack_info, stacklevel + 1)

    def debug(self, msg, *args, **kwargs):
        """Log a debug message with optional structured data."""
        self._log_with_extra(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log an info message with optional structured data."""
        self._log_with_extra(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log a warning message with optional structured data."""
        self._log_with_extra(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message with optional structured data."""
        self._log_with_extra(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log a critical message with optional structured data."""
        self._log_with_extra(logging.CRITICAL, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """Log an exception with traceback and optional structured data."""
        self._log_with_extra(logging.ERROR, msg, args, exc_info=exc_info, **kwargs)


# Register the custom logger class
logging.setLoggerClass(WipekitLogger)


def get_formatter(log_format: LogFormat, include_timestamp: bool = True) -> logging.Formatter:
    """Get the appropriate formatter based on the format specification.

    Args:
        log_format: The desired log format
        include_timestamp: Whether to include timestamps in logs

    Returns:
        A configured formatter instance
    """
    if log_format == LogFormat.JSON:
        return JsonFormatter(include_timestamp=include_timestamp)
    elif log_format == LogFormat.COMPACT:
        return CompactFormatter(include_timestamp=include_timestamp)
    else:  # TEXT format (default)
        if include_timestamp:
            return logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            return logging.Formatter(
                "[%(levelname)s] %(name)s: %(message)s"
            )


def configure_handler(handler: logging.Handler, log_format: LogFormat, level: LogLevel) -> None:
    """Configure a logging handler with the specified format and level.

    Args:
        handler: The handler to configure
        log_format: The format to use for logs
        level: The minimum log level for this handler
    """
    formatter = get_formatter(log_format)
    handler.setFormatter(formatter)
    handler.setLevel(level.value)


def create_handler(handler_type: LogHandler, **kwargs) -> Optional[logging.Handler]:
    """Create and configure a log handler of the specified type.

    Args:
        handler_type: The type of handler to create
        **kwargs: Additional configuration options for the handler

    Returns:
        A configured handler or None if creation failed
    """
    try:
        if handler_type == LogHandler.CONSOLE:
            return logging.StreamHandler(sys.stdout)

        elif handler_type == LogHandler.FILE:
            log_file = kwargs.get("log_file")
            if not log_file:
                raise ValueError("log_file parameter is required for FILE handler")
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            return logging.FileHandler(log_file)

        elif handler_type == LogHandler.ROTATING_FILE:
            log_file = kwargs.get("log_file")
            max_bytes = kwargs.get("max_bytes", 10 * 1024 * 1024)  # 10 MB default
            backup_count = kwargs.get("backup_count", 5)
            if not log_file:
                raise ValueError("log_file parameter is required for ROTATING_FILE handler")
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            return RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )

        elif handler_type == LogHandler.TIMED_ROTATING_FILE:
            log_file = kwargs.get("log_file")
            when = kwargs.get("when", "midnight")  # Default rotate at midnight
            interval = kwargs.get("interval", 1)    # Default rotate every day
            backup_count = kwargs.get("backup_count", 7)  # Keep a week of logs by default
            if not log_file:
                raise ValueError("log_file parameter is required for TIMED_ROTATING_FILE handler")
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            return TimedRotatingFileHandler(
                log_file, when=when, interval=interval, backupCount=backup_count
            )

        elif handler_type == LogHandler.SYSLOG:
            address = kwargs.get("address", "/dev/log")
            facility = kwargs.get("facility", SysLogHandler.LOG_USER)
            return SysLogHandler(address=address, facility=facility)

        else:
            raise ValueError(f"Unknown handler type: {handler_type}")

    except Exception as e:
        # Log to stderr since the logging system might not be set up yet
        print(f"Error creating log handler: {str(e)}", file=sys.stderr)
        return None


def configure_logger(
    level: LogLevel = LogLevel.INFO,
    format: LogFormat = LogFormat.TEXT,
    handlers: Optional[List[LogHandler]] = None,
    log_file: Optional[str] = None,
    rotation: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    module_levels: Optional[Dict[str, LogLevel]] = None,
) -> None:
    """Configure the global logging settings for the application.

    This function sets up the logging system according to the specified parameters.
    It should typically be called once at application startup.

    Args:
        level: The default log level for all loggers
        format: The format to use for log messages
        handlers: List of handlers to install (defaults to console only)
        log_file: Path to the log file (required for file-based handlers)
        rotation: Whether to use rotating file handler instead of basic file handler
        max_bytes: Maximum file size before rotation (for rotating handler)
        backup_count: Number of backup files to keep (for rotating handler)
        module_levels: Dictionary mapping module names to specific log levels
    """
    # Set default handlers if none provided
    if handlers is None:
        handlers = [LogHandler.CONSOLE]

    # Store configuration for future loggers
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = {
        "level": level,
        "format": format,
        "handlers": handlers,
        "log_file": log_file,
        "rotation": rotation,
        "max_bytes": max_bytes,
        "backup_count": backup_count,
        "module_levels": module_levels or {}
    }

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level.value)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:  
        root_logger.removeHandler(handler)

    # Add requested handlers
    for handler_type in handlers:
        handler_args = {
            "log_file": log_file,
            "max_bytes": max_bytes,
            "backup_count": backup_count
        }

        # Determine which file handler to use if file logging is enabled
        if handler_type in (LogHandler.FILE, LogHandler.ROTATING_FILE, LogHandler.TIMED_ROTATING_FILE):
            if not log_file:
                continue  # Skip file handlers if no log file specified

            # Override with rotating handler if requested
            if handler_type == LogHandler.FILE and rotation:
                handler_type = LogHandler.ROTATING_FILE

        # Create and add the handler
        handler = create_handler(handler_type, **handler_args)
        if handler:
            configure_handler(handler, format, level)
            root_logger.addHandler(handler)

    # Configure specific module levels if provided
    if module_levels:
        for module_name, module_level in module_levels.items():
            module_logger = logging.getLogger(module_name)
            module_logger.setLevel(module_level.value)

    # Prevent propagation of logs below the configured level to the console
    # This ensures that debug logs don't appear in the console when not wanted
    logging.getLogger().handlers[0].setLevel(level.value if handlers else logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module name.

    This function returns an existing logger if one exists with the given name,
    or creates a new one according to the global configuration.

    Args:
        name: The name of the module or component (e.g., "wipekit.anonymization")

    Returns:
        A configured logger instance
    """
    # Check if we've already created this logger
    if name in _LOGGERS:
        return _LOGGERS[name]

    # Create new logger
    logger = logging.getLogger(name)

    # Apply module-specific level if configured
    if _GLOBAL_CONFIG and "module_levels" in _GLOBAL_CONFIG:
        module_levels = _GLOBAL_CONFIG["module_levels"]
        if name in module_levels:
            logger.setLevel(module_levels[name].value)

    # Store for future retrieval
    _LOGGERS[name] = logger
    return logger
