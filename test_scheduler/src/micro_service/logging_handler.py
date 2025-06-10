import sys
import logging
import coloredlogs


def set_logger_config() -> logging.Logger:
    """
    Initializes a logger implementation logging messages in format: e.g.
    10:40:50 some_file.py:67 INFO: Message to log

    """
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logger = logging.getLogger(__name__)
    coloredlogs.install(level='INFO', logger=logger, isatty=True,
                        fmt='%(asctime)s %(filename)8s:%(lineno)d %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S')

    return logger


logger = set_logger_config()
