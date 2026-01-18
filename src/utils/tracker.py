"""
Processing Tracker Module
Handles logging, tracking, and exception management.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum

from src.config import config


class LogLevel(Enum):
    """Log levels for tracking."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """A single log entry."""
    timestamp: str
    level: LogLevel
    message: str
    exception: Optional[str] = None
    context: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "message": self.message,
            "exception": self.exception,
            "context": self.context
        }

    def __str__(self) -> str:
        """String representation for console output."""
        base = f"[{self.timestamp}] {self.level.value}: {self.message}"
        if self.exception:
            base += f"\n  Exception: {self.exception}"
        return base


class ProcessingTracker:
    """
    Tracks processing progress, logs events, and manages exceptions.
    Allows processing to continue even when individual files fail.
    """

    def __init__(self, log_to_file: bool = True, log_to_console: bool = True):
        """
        Initialize the tracker.

        Args:
            log_to_file: Whether to write logs to file.
            log_to_console: Whether to print logs to console.
        """
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.entries: List[LogEntry] = []
        self.errors: List[LogEntry] = []
        self.warnings: List[LogEntry] = []

        # Setup file logging
        if log_to_file:
            self._setup_file_logger()

    def _setup_file_logger(self) -> None:
        """Setup file-based logging."""
        output_dir = Path(config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        log_file = output_dir / config.log_filename

        # Configure logging
        self.logger = logging.getLogger("FileProcessor")
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def _create_entry(
        self,
        level: LogLevel,
        message: str,
        exception: Optional[Exception] = None,
        context: Dict = None
    ) -> LogEntry:
        """Create a log entry."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            message=message,
            exception=str(exception) if exception else None,
            context=context or {}
        )
        self.entries.append(entry)

        if level == LogLevel.ERROR or level == LogLevel.CRITICAL:
            self.errors.append(entry)
        elif level == LogLevel.WARNING:
            self.warnings.append(entry)

        return entry

    def _output(self, entry: LogEntry) -> None:
        """Output a log entry to configured destinations."""
        if self.log_to_console:
            print(str(entry))

        if self.log_to_file and hasattr(self, 'logger'):
            log_method = getattr(self.logger, entry.level.value.lower())
            log_method(entry.message)
            if entry.exception:
                self.logger.error(f"Exception: {entry.exception}")

    def log_debug(self, message: str, context: Dict = None) -> None:
        """Log a debug message."""
        entry = self._create_entry(LogLevel.DEBUG, message, context=context)
        self._output(entry)

    def log_info(self, message: str, context: Dict = None) -> None:
        """Log an info message."""
        entry = self._create_entry(LogLevel.INFO, message, context=context)
        self._output(entry)

    def log_warning(self, message: str, context: Dict = None) -> None:
        """Log a warning message."""
        entry = self._create_entry(LogLevel.WARNING, message, context=context)
        self._output(entry)

    def log_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Dict = None
    ) -> None:
        """Log an error message with optional exception."""
        entry = self._create_entry(LogLevel.ERROR, message, exception, context)
        self._output(entry)

    def log_critical(
        self,
        message: str,
        exception: Optional[Exception] = None,
        context: Dict = None
    ) -> None:
        """Log a critical error."""
        entry = self._create_entry(LogLevel.CRITICAL, message, exception, context)
        self._output(entry)

    def get_error_count(self) -> int:
        """Get the number of errors logged."""
        return len(self.errors)

    def get_warning_count(self) -> int:
        """Get the number of warnings logged."""
        return len(self.warnings)

    def get_summary(self) -> Dict:
        """Get a summary of all logged events."""
        return {
            "total_entries": len(self.entries),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }

    def get_errors_report(self) -> str:
        """Generate a formatted report of all errors."""
        if not self.errors:
            return "No errors recorded."

        lines = ["=" * 60]
        lines.append("ERROR REPORT")
        lines.append("=" * 60)

        for i, error in enumerate(self.errors, 1):
            lines.append(f"\n{i}. [{error.timestamp}]")
            lines.append(f"   Message: {error.message}")
            if error.exception:
                lines.append(f"   Exception: {error.exception}")
            if error.context:
                lines.append(f"   Context: {error.context}")

        lines.append("\n" + "=" * 60)
        lines.append(f"Total Errors: {len(self.errors)}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all logged entries."""
        self.entries.clear()
        self.errors.clear()
        self.warnings.clear()
