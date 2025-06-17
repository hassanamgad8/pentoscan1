import logging
import sys
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    Configure logging with the specified level.
    Sets up both file and console handlers.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create file handler
    log_filename = f"logs/pentoscan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger 