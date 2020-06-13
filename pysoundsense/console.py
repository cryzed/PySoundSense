import argparse
import pprint

from loguru import logger

from . import (
    ExitCode,
    APPLICATION_NAME,
    __version__,
    LOGGING_LEVEL,
    LOG_PATH,
    LOG_COMPRESSION,
    LOG_ROTATION,
    LOG_RETENTION,
)
from .sounds import yield_sounds
from .gamelog import watch_game_log


def get_argument_parser() -> argparse.ArgumentParser:
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("pack_path", metavar="pack-path", help="Path to the sound pack")
    parser.add_argument("game_log", metavar="game-log", help="Path to the game log")
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=1.0,
        help="Frequency at which the game log is checked for updates",
    )

    parser.add_argument(
        "--logging-level",
        "-l",
        default=LOGGING_LEVEL,
        choices={"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"},
        help="Logging level used on stderr",
    )
    parser.add_argument("--log-path", "-lp", default=LOG_PATH, help="Log file path")
    parser.add_argument(
        "--log-compression",
        "-lc",
        default=LOG_COMPRESSION,
        choices={
            "gz",
            "bz2",
            "xz",
            "lzma",
            "tar",
            "tar.gz",
            "tar.bz2",
            "tar.xz",
            "zip",
        },
        help="Log file compression",
    )
    parser.add_argument(
        "--log-rotation", "-lr", default=LOG_ROTATION, help="Log rotation interval",
    )
    parser.add_argument(
        "--log-retention", "-lR", default=LOG_RETENTION, help="Log retention time span",
    )
    return parser


def run(arguments: argparse.Namespace) -> ExitCode:
    logger.info("Running {} v{}", APPLICATION_NAME, __version__)
    all_sounds = list(yield_sounds(arguments.pack_path))

    for line in watch_game_log(arguments.game_log, interval=arguments.interval):
        logger.info(line)
        for sounds in all_sounds:
            if sound := sounds.match(line):
                pprint.pprint(sound)

    return ExitCode.Success
