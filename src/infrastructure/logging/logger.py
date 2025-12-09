import logging
import sys

from src.infrastructure.configuration.settings import Settings


def setup_logging(settings: Settings) -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("rag_template")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(f"rag_template.{name}")
    return logging.getLogger("rag_template")
