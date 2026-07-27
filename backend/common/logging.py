"""
AgriDecision AI - Common Logging Configuration
Provides JSON structured logging suitable for Loki/Elasticsearch.
"""
import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter injecting standard contextual fields."""
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # This uses the current time in ISO8601 format
            log_record['timestamp'] = self.formatTime(record, self.datefmt)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


def setup_logging(service_name: str, log_level: str = "INFO") -> None:
    """
    Configure root logger with JSON formatting.
    Call this at the application entrypoint (e.g., main.py).
    """
    logger = logging.getLogger()
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    log_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={"levelname": "level", "name": "logger"}
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Inject service name into all logs
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.service = service_name
        return record

    logging.setLogRecordFactory(record_factory)

    # Suppress overly verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)
