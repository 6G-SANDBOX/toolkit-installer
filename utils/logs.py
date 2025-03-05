import logging
import os
import sys

LOG_LEVELS_AND_FORMATS = {
    "DEBUG": ("\x1b[38;21m", logging.DEBUG),
    "INFO": ("\x1b[38;5;39m", logging.INFO),
    "WARNING": ("\x1b[38;5;226m", logging.WARNING),
    "ERROR": ("\x1b[38;5;196m", logging.ERROR),
    "CRITICAL": ("\x1b[31;1m", logging.CRITICAL),
}

RESET_COLOR = "\x1b[0m"


class CustomFormatter(logging.Formatter):
    """
    Logging formatter with color support
    """

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt

    def format(self, record):
        log_color, _ = LOG_LEVELS_AND_FORMATS.get(record.levelname, ("", logging.INFO))
        log_fmt = log_color + self.fmt + RESET_COLOR
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def msg(level: str, message: str) -> None:
    """
    Logs a message with a specific level and optional color

    :param level: Logging level (debug, info, warning, error, critical)
    :param message: Message to log
    """
    level = level.upper()
    logger = logging.getLogger("toolkit")

    log_func = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical,
    }.get(level, logger.info)

    log_func(message)

    if level in {"ERROR", "CRITICAL"}:
        sys.exit(1)


def setup_logger() -> None:
    """
    Configures the global logger with color formatting
    """
    log_format = "[%(asctime)s] - [%(levelname)s] - %(message)s"
    log_level_name = os.getenv("TOOLKIT_INSTALLER_LOG_LEVEL", "INFO").upper()
    _, log_level = LOG_LEVELS_AND_FORMATS.get(
        log_level_name, LOG_LEVELS_AND_FORMATS["INFO"]
    )

    logger = logging.getLogger("toolkit")

    formatter = CustomFormatter(log_format)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(handler)
    logger.propagate = False
