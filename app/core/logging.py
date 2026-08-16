import logging
import logging.config
import sys
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures application-wide logging formats and log levels.
    Ensures FastAPI/Uvicorn, SQLAlchemy, Qdrant, and custom app loggers
    use a consistent, structured output.
    """
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s | %(levelname)-8s | uvicorn.access - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "level": log_level,
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "access",
                "level": log_level,
            },
        },
        "loggers": {
            # Core Application Loggers
            "app": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            # Uvicorn Server Loggers
            "uvicorn": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access_console"],
                "level": log_level,
                "propagate": False,
            },
            # Third-Party Framework Loggers
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",  
                "propagate": False,
            },
            "qdrant_client": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "httpx": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }

    logging.config.dictConfig(logging_config)