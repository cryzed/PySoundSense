# See "SoundSense.ipynb" for research on used tags and attributes
# http://df.zweistein.cz/soundsense/
# http://dwarffortresswiki.org/index.php/Utility:SoundSense/Documentation#Customization

import dataclasses
import enum
import os
import pathlib
import re
import typing as T

import bs4
from loguru import logger

from .errors import ParseError
from .types_ import Path

# Used to warn about unknown attributes
_KNOWN_ATTRIBUTES = {
    "sounds": {
        "defaultansicolor",
        "defaultansiformat",
        "defaultansipattern",
        "strictattributions",
    },
    "sound": {
        "ansiformat",
        "ansipattern",
        "channel",
        "concurency",
        "concurrency",
        "delay",
        "haltonmatch",
        "logpattern",
        "loop",
        "playbackthreshhold",
        "playbackthreshold",
        "propability",
        "probability",
        "randombalance",
        "timeout",
    },
    "soundfile": {
        "balanceadjustment",
        "delay",
        "filename",
        "playlist",
        "randombalance",
        "volumeadjustment",
        "weight",
    },
}

_REQUIRED_ATTRIBUTES = {
    "sounds": (),
    "sound": ("logpattern",),
    "soundfile": ("filename",),
}

# Fix up typos and translate attribute names into snake-case
_ATTRIBUTE_TRANSLATION = {
    "defaultansicolor": "default_ansi_color",
    "defaultansiformat": "default_ansi_format",
    "defaultansipattern": "default_anis_pattern",
    "strictattributions": "strict_attributions",
    "ansiformat": "ansi_format",
    "ansipattern": "ansi_pattern",
    "concurency": "concurrency",
    "haltonmatch": "halt_on_match",
    "logpattern": "log_pattern",
    "playbackthreshhold": "playback_threshold",
    "propability": "probability",
    "randombalance": "random_balance",
    "volumeadjustment": "volume_adjustment",
}


class Loop(enum.Enum):
    Start = "start"
    Stop = "stop"


class PlaybackThreshold(enum.IntEnum):
    Everything = 4
    Fluff = 3
    Important = 2
    Critical = 1
    Nothing = 0


_ATTRIBUTE_TYPES: T.Dict[T.Tuple[str, str], T.Callable[[T.Any], T.Any]] = {
    ("sounds", "strict_attributions"): bool,
    ("sound", "log_pattern"): re.compile,
    ("sound", "concurrency"): int,
    ("sound", "delay"): int,
    ("sound", "playback_threshold"): lambda value: PlaybackThreshold(
        min(4, int(value))
    ),
    ("sound", "probability"): int,
    ("sound", "timeout"): int,
    ("sound", "halt_on_match"): bool,
    ("sound", "random_balance"): bool,
    # Hack to translate "true" to "start", which can be found in the official SoundSense
    # pack files
    ("sound", "loop"): lambda value: Loop("start" if value == "true" else value),
    ("soundfile", "weight"): int,
}


@dataclasses.dataclass
class SoundFile:
    file_name: str
    balance_adjustment: int = 0
    delay: int = 0
    playlist: bool = False
    random_balance: bool = False
    volume_adjustment: int = 0
    weight: int = 100

    def __hash__(self) -> int:
        return hash(self.file_name)


@dataclasses.dataclass
class Sound:
    log_pattern: T.Pattern
    ansi_format: str = ""
    ansi_pattern: str = ""
    channel: T.Optional[str] = None
    concurrency: T.Optional[int] = None
    delay: int = 0
    halt_on_match: bool = False
    loop: T.Optional[Loop] = None
    playback_threshold: PlaybackThreshold = PlaybackThreshold.Nothing
    probability: int = 100
    random_balance: bool = False
    timeout: int = 0

    files: T.List[SoundFile] = dataclasses.field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.log_pattern)


@dataclasses.dataclass
class Sounds:
    path: str

    default_ansi_color: str = ""
    default_ansi_format: str = ""
    default_ansi_pattern: str = ""
    strict_attributions: T.Optional[bool] = None

    sounds: T.List[Sound] = dataclasses.field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.path)


def _get_required_attributes(element: bs4.Tag) -> T.List[T.Any]:
    attributes = []
    for attribute in _REQUIRED_ATTRIBUTES[element.name]:
        value = element.attrs.get(attribute)
        if value is None:
            raise ParseError(
                f"Missing required {element.name!r}-attribute {attribute!r}"
            )
        key = _ATTRIBUTE_TRANSLATION.get(attribute, attribute)
        type_ = _ATTRIBUTE_TYPES.get((element.name, key), str)
        attributes.append(type_(value))
    return attributes


def _get_optional_attributes(element: bs4.Tag) -> T.Dict[str, T.Any]:
    attributes = {}
    for attribute, value in element.attrs.items():
        if attribute not in _KNOWN_ATTRIBUTES[element.name]:
            logger.warning("Unknown {!r}-attribute {!r}", element.name, attribute)
            continue

        if attribute in _REQUIRED_ATTRIBUTES[element.name]:
            continue

        key = _ATTRIBUTE_TRANSLATION.get(attribute, attribute)
        type_ = _ATTRIBUTE_TYPES.get((element.name, key), str)
        attributes[key] = type_(value)

    return attributes


def parse_sounds(path: Path) -> Sounds:
    path = os.fspath(path)
    with open(path, "rb") as file:
        data = file.read()

    soup = bs4.BeautifulSoup(data, features="lxml")
    sounds_element = soup.sounds
    if not sounds_element:
        raise ParseError(f'Missing required top-level "sounds"-element')

    sounds = Sounds(str(path), *_get_required_attributes(sounds_element))
    for key, value in _get_optional_attributes(sounds_element).items():
        setattr(sounds, key, value)

    for sound_element in sounds_element("sound"):
        sound = Sound(*_get_required_attributes(sound_element))
        for key, value in _get_optional_attributes(sound_element).items():
            setattr(sound, key, value)
        sounds.sounds.append(sound)

        for file_element in sound_element("soundfile"):
            sound_file = SoundFile(*_get_required_attributes(file_element))
            for key, value in _get_optional_attributes(file_element).items():
                setattr(sound_file, key, value)
            sound.files.append(sound_file)

    return sounds


def yield_sounds(pack_path: Path) -> T.Generator[Sounds, None, None]:
    for path in pathlib.Path(os.fspath(pack_path)).rglob("*.xml"):
        try:
            sounds = parse_sounds(str(path))
        except ParseError as error:
            logger.warning("Error: {} for {!r}", error, str(path))
            continue

        # Adjust file_name to contain absolute path, relative to the XML path
        for sound in sounds.sounds:
            for file in sound.files:
                file.file_name = str(path.parent / file.file_name)

        yield sounds
