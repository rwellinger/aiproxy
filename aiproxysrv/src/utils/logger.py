"""
Centralized logging configuration using loguru.
Replaces all print() statements with structured logging.
"""
import logging
import sys

from loguru import logger

from config.settings import LOG_LEVEL


# Remove default logger
logger.remove()

# Custom formatter function to handle extra fields
def format_record(record):
    """
    Custom formatter that displays extra fields (error, error_type, stacktrace)
    for ERROR and CRITICAL level logs.
    """
    # Base format
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add extra fields for ERROR/CRITICAL logs
    if record["level"].name in ("ERROR", "CRITICAL"):
        extra = record["extra"]

        if "error_type" in extra:
            format_str += "\n  <yellow>└─ Type:</yellow> <red>{extra[error_type]}</red>"

        if "error" in extra:
            format_str += "\n  <yellow>└─ Error:</yellow> <red>{extra[error]}</red>"

        if "stacktrace" in extra and extra["stacktrace"]:
            # Add stacktrace with indentation
            format_str += "\n  <yellow>└─ Stacktrace:</yellow>\n<red>{extra[stacktrace]}</red>"

        # Show other extra fields if present (except the ones we already handled)
        other_extras = {k: v for k, v in extra.items()
                       if k not in ("error_type", "error", "stacktrace") and not k.startswith("_")}
        if other_extras:
            for key, value in other_extras.items():
                format_str += f"\n  <yellow>└─ {key}:</yellow> {{extra[{key}]}}"

    format_str += "\n"
    return format_str

# Console handler: INFO and above with colors
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format=format_record,
    colorize=True,
)

# Flask-Logging auf loguru umleiten
class LoguruHandler(logging.Handler):
    def emit(self, record):
        # LogRecord in loguru format umwandeln
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Frame für korrekte Anzeige finden
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Celery-Logging auf loguru umleiten
class CeleryInterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

# Export configured logger
__all__ = ["logger"]
