import enum
import os
import sys

import appdirs
from loguru import logger

__version__ = "0.1.0"

APPLICATION_NAME = "PySoundSense"
APPLICATION_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIRECTORY = appdirs.user_config_dir(APPLICATION_NAME)
CACHE_DIRECTORY = appdirs.user_cache_dir(APPLICATION_NAME)
LOG_DIRECTORY = appdirs.user_log_dir(APPLICATION_NAME)

LOG_PATH = os.path.join(LOG_DIRECTORY, "{}.log".format(APPLICATION_NAME))
LOGGING_LEVEL = "INFO"
LOG_ROTATION = "1 day"
LOG_COMPRESSION = "zip"
LOG_RETENTION = "1 month"


class ExitCode(enum.IntEnum):
    Success = 0
    Failure = 1


def initialize(
    log_path: str = LOG_PATH,
    logging_level: str = LOGGING_LEVEL,
    log_rotation: str = LOG_ROTATION,
    log_compression: str = LOG_COMPRESSION,
    log_retention: str = LOG_RETENTION,
) -> None:
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
    os.makedirs(CACHE_DIRECTORY, exist_ok=True)
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    logger.remove()
    logger.add(sys.stderr, level=logging_level)
    logger.add(
        log_path,
        level="DEBUG",
        rotation=log_rotation,
        compression=log_compression,
        retention=log_retention,
    )
