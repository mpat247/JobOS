# logging_config.py

import logging
from colorlog import ColoredFormatter

def setup_logging():
    # Remove all existing handlers (avoids duplicate logs)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create console handler with colored output
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configure root logger (affects all libraries, celery, etc.)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler]
    )

    # Also return a named logger if you want to use one
    return logging.getLogger("scraper")


# Optional test
if __name__ == "__main__":
    logger = setup_logging()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
