import logging
import coloredlogs


def initialize_logging():
    """
    Initializes a logger with a specific format and log level.

    The log format is: "time, loglevel [filename:line] message".
    The log level is set to DEBUG, and coloredlogs is used to enhance readability.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create a logger object.
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.DEBUG
    )

    coloredlogs.install(level='DEBUG')
    coloredlogs.install(level='DEBUG', logger=logger)
    return logger
