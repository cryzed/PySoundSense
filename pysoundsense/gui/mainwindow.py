import pathlib
import threading
import typing as T

from PySide2.QtCore import QThread, QObject, Signal, QUrl
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtWidgets import QMainWindow
from loguru import logger

from .mainwindow_ui import Ui_MainWindow
from ..gamelog import watch_game_log
from ..sounds import yield_sounds, Sounds
from ..types_ import Path


class GameLogWatcher(QThread):
    new_log = Signal(str)

    def __init__(self, game_log_path: Path, parent: T.Optional[QObject] = None):
        self.game_log_path = game_log_path
        self._stop_event = threading.Event()
        super().__init__(parent)

    def stop(self):
        self._stop_event.set()

    @logger.catch
    def run(self):
        for line in watch_game_log(self.game_log_path):
            if self._stop_event.is_set():
                break

            self.new_log.emit(line)


class MainWindow(QMainWindow):
    def __init__(
        self,
        game_log_path: T.Optional[Path] = None,
        pack_path: T.Optional[Path] = None,
    ) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.volume.valueChanged.connect(self.on_volume_changed)
        self.ui.channels.volume_changed.connect(self.on_channel_volume_changed)

        self.game_log_watcher: T.Optional[GameLogWatcher] = None
        self.sounds: T.List[Sounds] = []
        self.media_player = QMediaPlayer()

        game_log_path = pathlib.Path(game_log_path)
        if game_log_path.is_file():
            self.load_game_log(game_log_path)

        pack_path = pathlib.Path(pack_path)
        if pack_path.is_dir():
            self.load_sounds(pack_path)

    def on_new_game_log(self, line: str) -> None:
        logger.info("Game log: {!r}", line)
        self.ui.log.append(line)

        for sounds in self.sounds:
            sound = sounds.match(line)
            if not sound:
                continue

            file = sound.get_file()
            if not file:
                continue

            # TODO: Channel etc. logic
            self.media_player.setMedia(QUrl.fromLocalFile(file.file_name))
            self.media_player.play()

    def on_volume_changed(self, volume: int) -> None:
        logger.debug("Volume: {}%", volume)

    def on_channel_volume_changed(self, channel: str, volume: int) -> None:
        logger.debug("{!r} channel volume: {}%", channel, volume)

    def load_game_log(self, path: Path) -> None:
        if self.game_log_watcher:
            self.game_log_watcher.stop()

        self.game_log_watcher = GameLogWatcher(path, self)
        self.game_log_watcher.new_log.connect(self.on_new_game_log)
        self.game_log_watcher.start()

    def load_sounds(self, path: Path) -> None:
        channels = set()
        for sounds in yield_sounds(path):
            self.sounds.append(sounds)
            for sound in sounds.sounds:
                channels.add(sound.channel or "default")

        for channel in sorted(channels):
            self.ui.channels.add_channel(channel)
