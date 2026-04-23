"""Log utilities."""

import logging
import sys

from rich.logging import RichHandler
from rich.text import Text

from src.constants import DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL


class ColonRichHandler(RichHandler):
    """RichHandler that adds a colon after the log level with uvicorn-style spacing."""

    LEVEL_COLORS = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bright_red",
    }

    def get_level_text(self, record: logging.LogRecord) -> Text:
        level_name = record.levelname
        level_text = f"{level_name}:".ljust(9)
        style = self.LEVEL_COLORS.get(level_name, "")
        return Text.styled(level_text, style)


def create_log_handler() -> logging.Handler:
    """
    Create and return a configured log handler based on TTY availability.

    If stderr is connected to a terminal (TTY), returns a RichHandler for
    rich-formatted console output. If not, returns a StreamHandler with
    plain-text formatting suitable for non-TTY environments (e.g., containers).

    Returns:
        logging.Handler: A configured handler instance (RichHandler or StreamHandler).
    """
    if sys.stderr.isatty():
        return ColonRichHandler(show_time=False)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger configured for Rich console output.

    The returned logger has its level set to DEFAULT_LOG_LEVEL, its handlers
    replaced with a single handler (RichHandler for TTY or StreamHandler for
    non-TTY), and propagation to ancestor loggers disabled.

    Parameters:
    ----------
        name (str): Name of the logger to retrieve or create.

    Returns:
    -------
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.handlers = [create_log_handler()]
    logger.propagate = False
    logger.setLevel(getattr(logging, DEFAULT_LOG_LEVEL))
    return logger
