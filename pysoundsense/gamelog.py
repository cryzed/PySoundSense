import io
import time
import typing as T

from .types_ import Path

# https://youtu.be/snbt0PxRvpk?t=3369
# https://github.com/Pidgeot/python-lnp/pull/171#issuecomment-646338011
_GAME_LOG_ENCODING = "CP437"


def watch_game_log(path: Path) -> T.Generator[str, None, None]:
    with open(path, encoding=_GAME_LOG_ENCODING) as file:
        file.seek(0, io.SEEK_END)
        while True:
            while line := file.readline().strip():
                yield line

            time.sleep(0.01)
