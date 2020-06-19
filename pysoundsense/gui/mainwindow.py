import pathlib
import threading
import typing as T

from PySide2.QtCore import QThread, QObject, Signal
from PySide2.QtWidgets import QMainWindow
from loguru import logger

from .mainwindow_ui import Ui_MainWindow
from .utils import logarithmic_to_linear_volume, load_dwarf_fortress_font
from ..gamelog import watch_game_log
from ..sounds import yield_sounds, Sound
from ..types_ import Path


class GameLogWatcher(QThread):
    new_log = Signal(str)

    def __init__(self, game_log_path: Path, parent: T.Optional[QObject] = None):
        super().__init__(parent)
        self.game_log_path = game_log_path
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    @logger.catch
    def run(self):
        for line in watch_game_log(self.game_log_path):
            if self._stop_event.is_set():
                break

            # noinspection PyUnresolvedReferences
            self.new_log.emit(line)


class MainWindow(QMainWindow):
    def __init__(
        self,
        game_log_path: T.Optional[Path] = None,
        pack_path: T.Optional[Path] = None,
    ) -> None:
        super().__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._ui.volume.valueChanged.connect(self.on_volume_changed)
        font = load_dwarf_fortress_font()
        self._ui.log.setFont(font)
        self._game_log_watcher: T.Optional[GameLogWatcher] = None
        self._sounds: T.List[Sound] = []

        if game_log_path:
            game_log_path = pathlib.Path(game_log_path)
            if game_log_path.is_file():
                self.load_game_log(game_log_path)

        if pack_path:
            pack_path = pathlib.Path(pack_path)
            if pack_path.is_dir():
                self.load_sounds(pack_path)

    def on_new_game_log(self, line: str) -> None:
        logger.debug("Game log: {!r}", line)
        self._ui.log.append(line)
        for sound in self._sounds:
            if sound.log_pattern.match(line):
                self._ui.channels.play_sound(sound)
                if sound.halt_on_match:
                    break

    def on_volume_changed(self, volume: int) -> None:
        linear_volume = logarithmic_to_linear_volume(volume)
        logger.trace("Adjusting main volume: {!r}", linear_volume)
        self._ui.channels.set_volume(linear_volume)

    def load_game_log(self, path: Path) -> None:
        if self._game_log_watcher:
            self._game_log_watcher.stop()

        self._game_log_watcher = GameLogWatcher(path, self)
        # noinspection PyUnresolvedReferences
        self._game_log_watcher.new_log.connect(self.on_new_game_log)  # type: ignore
        self._game_log_watcher.start()

    def load_sounds(self, path: Path) -> None:
        channels: T.Set[T.Optional[str]] = set()

        for sounds_xml in yield_sounds(path):
            for sound in sounds_xml.sounds:
                sound.ansi_format = sound.ansi_format or sounds_xml.default_ansi_format
                sound.ansi_pattern = (
                    sound.ansi_pattern or sounds_xml.default_ansi_pattern
                )

                channels.add("Default" if sound.channel is None else sound.channel)
                self._sounds.append(sound)

        if "Default" in channels:
            self._ui.channels.add_channel("Default")
            channels.remove("Default")

        for channel in sorted(channels):
            self._ui.channels.add_channel(channel)
