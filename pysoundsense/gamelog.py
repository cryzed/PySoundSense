import io
import time
import typing as T

from .types_ import Path


def watch_game_log(
    path: Path, encoding: str = "CP850", interval: float = 1.0
) -> T.Generator[str, None, None]:
    with open(path, encoding=encoding) as file:
        file.seek(0, io.SEEK_END)
        while True:
            while line := file.readline().strip():
                yield line

            time.sleep(interval)
