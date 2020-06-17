import io
import time
import typing as T

from .types_ import Path

_GAME_LOG_ENCODING = "CP850"


def watch_game_log(path: Path) -> T.Generator[str, None, None]:
    with open(path, encoding=_GAME_LOG_ENCODING) as file:
        file.seek(0, io.SEEK_END)
        while True:
            while line := file.readline().strip():
                yield line

            time.sleep(0.01)
