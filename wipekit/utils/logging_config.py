# wipekit - Logging configuration utilities
# Copyright (c) 2025 Wipekit Authors
# MIT License

"""
Logging Configuration Utilities
=============================

This module provides ready-to-use configurations for the wipekit logging system.
It includes common logging setups for different environments and use cases.

Example:
    >>> from wipekit.utils.logging_config import configure_production_logging
    >>> configure_production_logging(log_dir="/var/log/myapp")
"""

import os
from typing import Dict, Optional

from wipekit.logging import (
    configure_logger, 
    LogLevel, 
    LogFormat, 
    LogHandler,
    get_logger
)


def configure_development_logging() -> None:
    """
    Configure logging for development environment.

    Features:
    - Console output with detailed messages
    - Debug level logging
    - Text format for readability
    """
    configure_logger(
        level=LogLevel.DEBUG,
        format=LogFormat.TEXT,
        handlers=[LogHandler.CONSOLE]
    )

    logger = get_logger("wipekit")
    logger.info("Development logging configured successfully")


def configure_testing_logging() -> None:
    """
    Configure logging for testing environment.

    Features:
    - Minimal logging (warnings and errors only)
    - Compact format
    - Console output only
    """
    configure_logger(
        level=LogLevel.WARNING,
        format=LogFormat.COMPACT,
        handlers=[LogHandler.CONSOLE]
    )

    logger = get_logger("wipekit")
    logger.info("Testing logging configured successfully")


def configure_production_logging(
    log_dir: str, 
    log_level: LogLevel = LogLevel.INFO,
    module_levels: Optional[Dict[str, LogLevel]] = None
) -> None:
    """
    Configure logging for production environment.

    Features:
    - JSON formatted logs for machine processing
    - Daily rotating file logs
    - Console output for container environments
    - Configurable module-specific log levels

    Args:
        log_dir: Directory to store log files
        log_level: Default log level for all modules
        module_levels: Optional dict mapping module names to specific log levels
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Default module-specific levels if not provided
    if module_levels is None:
        module_levels = {
            "wipekit.anonymization": LogLevel.INFO,
            "wipekit.read": LogLevel.INFO,
            "wipekit.utils": LogLevel.WARNING
        }

    configure_logger(
        level=log_level,
        format=LogFormat.JSON,
        handlers=[LogHandler.CONSOLE, LogHandler.TIMED_ROTATING_FILE],
        log_file=os.path.join(log_dir, "wipekit.log"),
        rotation=True,
        backup_count=30,  # Keep a month of logs
        module_levels=module_levels
    )

    logger = get_logger("wipekit")
    logger.info("Production logging configured successfully", 
               extra={"log_dir": log_dir, "default_level": log_level.name})


def configure_high_performance_logging(
    log_dir: str,
    enable_console: bool = False
) -> None:
    """
    Configure logging optimized for high-throughput applications.

    Features:
    - Compact log format to minimize I/O
    - Size-based log rotation
    - Optional console output (disabled by default)
    - Warning level for most modules to reduce logging overhead

    Args:
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Define handlers
    handlers = [LogHandler.ROTATING_FILE]
    if enable_console:
        handlers.append(LogHandler.CONSOLE)

    # Configure with performance settings
    configure_logger(
        level=LogLevel.WARNING,
        format=LogFormat.COMPACT,
        handlers=handlers,
        log_file=os.path.join(log_dir, "wipekit-perf.log"),
        max_bytes=50 * 1024 * 1024,  # 50 MB per file
        backup_count=5,
        module_levels={
            # Critical paths with minimal logging
            "wipekit.core": LogLevel.WARNING,
            "wipekit.read": LogLevel.WARNING,
            "wipekit.utils": LogLevel.ERROR,
            # Less critical paths
            "wipekit.anonymization": LogLevel.INFO
        }
    )

    logger = get_logger("wipekit")
    logger.info("High-performance logging configured")
