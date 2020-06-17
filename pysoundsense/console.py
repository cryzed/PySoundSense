import argparse

from PySide2.QtWidgets import QApplication
from loguru import logger

from . import (
    APPLICATION_NAME,
    __version__,
    LOGGING_LEVEL,
    LOG_PATH,
    LOG_COMPRESSION,
    LOG_ROTATION,
    LOG_RETENTION,
)
from .gui.mainwindow import MainWindow


def get_argument_parser() -> argparse.ArgumentParser:
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "game_log_path", metavar="game-log", help="Path to the game log", nargs="?"
    )
    parser.add_argument(
        "pack_path", metavar="pack", help="Path to the sound pack", nargs="?"
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


def run(arguments: argparse.Namespace) -> int:
    logger.info("Running {} v{}", APPLICATION_NAME, __version__)
    application = QApplication()
    window = MainWindow(arguments.game_log_path, arguments.pack_path)
    window.show()
    return application.exec_()
