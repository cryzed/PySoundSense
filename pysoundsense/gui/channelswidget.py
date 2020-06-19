import collections
import random
import time
import typing as T

from PySide2 import QtCore
from PySide2.QtCore import QObject, Qt, QUrl, QTimer
from PySide2.QtMultimedia import QMediaPlayer, QAudio, QMediaPlaylist
from PySide2.QtWidgets import QWidget, QLabel, QSlider, QLayoutItem, QComboBox
from loguru import logger

from .channelswidget_ui import Ui_ChannelsWidget
from .utils import (
    logarithmic_to_linear_volume,
    add_decibel_to_linear_volume,
)
from ..sounds import Sound, Loop, PlaybackThreshold
from ..types_ import Number


class Channel(QObject):
    def __init__(
        self, name: T.Optional[str], parent: T.Optional[QObject] = None
    ) -> None:
        super().__init__(parent)
        self.name = name
        self.slider_volume: Number = 100
        self.threshold = PlaybackThreshold.Everything

        self._loop_sound: T.Optional[Sound] = None
        self._loop_player = QMediaPlayer(self)
        self._loop_volume_adjustment: Number = 0
        self._loop_player.setAudioRole(QAudio.GameRole)
        self._loop_playlist = QMediaPlaylist(self)
        self._loop_playlist.setPlaybackMode(QMediaPlaylist.CurrentItemOnce)
        self._loop_player.setPlaylist(self._loop_playlist)
        self._loop_player.stateChanged.connect(self._on_loop_player_state_changed)

        self._one_shot_player = QMediaPlayer(self)
        self._one_shot_volume_adjustment: Number = 0
        self._one_shot_player.setAudioRole(QAudio.GameRole)
        self._one_shot_player.stateChanged.connect(
            self._on_one_shot_player_state_changed
        )

    @property
    def is_playing(self):
        return (
            self._loop_player.state() == QMediaPlayer.PlayingState
            or self._one_shot_player.state() == QMediaPlayer.PlayingState
        )

    def _on_loop_player_state_changed(self, state: QMediaPlayer.State) -> None:
        logger.trace("Loop player state changed: {!r}", state)
        if state != QMediaPlayer.StoppedState:
            return

        decibel = -self._loop_volume_adjustment
        logger.trace("Readjusting loop player volume by {}db", decibel)
        self.adjust_player_volume_by_decibel(self._loop_player, decibel)
        self._loop_volume_adjustment = 0

        # Loop playlist is empty
        if not self._loop_playlist.mediaCount():
            logger.trace("Loop playlist is empty, not queueing a new file")
            return

        # This shouldn't ever happen, it's just here to make mypy happy
        if not self._loop_sound:
            return

        file = random.choices(
            self._loop_sound.files, [file.weight for file in self._loop_sound.files]
        )[0]
        index = self._loop_sound.files.index(file)
        logger.trace(
            "Loop player playing file: {!r} at playlist index: {}", file, index,
        )
        self._loop_playlist.setCurrentIndex(index)
        self._loop_player.play()

    def _on_one_shot_player_state_changed(self, state: QMediaPlayer.State) -> None:
        logger.trace("One-shot player state changed: {!r}", state)
        if state != QMediaPlayer.StoppedState:
            return

        decibel = -self._one_shot_volume_adjustment
        logger.trace("Readjusting one-shot player volume by {}db", decibel)
        self.adjust_player_volume_by_decibel(self._one_shot_player, decibel)
        self._one_shot_volume_adjustment = 0

        logger.trace("One-shot player stopped, resuming loop player")
        self._loop_player.play()

    def play_sound(self, sound: Sound) -> None:
        if sound.playback_threshold > self.threshold:
            logger.trace("Ignoring sound {!r} because of threshold", sound)
            return

        if sound.loop is Loop.Start:
            self._loop_sound = sound
            # New looping sound, rebuild playlist
            self._loop_playlist.clear()
            for file in sound.files:
                media = QUrl.fromLocalFile(file.file_name)
                self._loop_playlist.addMedia(media)

            # Select file based on weight and set the matching playlist index
            weights = [file.weight for file in sound.files]
            file = random.choices(sound.files, weights)[0]
            index = sound.files.index(file)
            self._loop_playlist.setCurrentIndex(index)

            logger.trace("Adjusting loop player volume by {}db", file.volume_adjustment)
            self._loop_volume_adjustment = self.adjust_player_volume_by_decibel(
                self._loop_player, file.volume_adjustment
            )
            logger.trace(
                "Adjusted One-shot player volume by {}db", self._loop_volume_adjustment
            )
            self._loop_player.play()
            logger.trace(
                "Loop player playing file: {!r} at playlist index: {}", file, index,
            )
            return
        if sound.loop is Loop.Stop:
            logger.trace("Stopping loop player")
            self._loop_sound = None
            self._loop_playlist.clear()
            self._loop_player.stop()
        else:
            logger.trace("Pausing loop player for one-shot sound")
            self._loop_player.pause()

        file = random.choices(sound.files, [file.weight for file in sound.files])[0]
        media = QUrl.fromLocalFile(file.file_name)
        self._one_shot_player.setMedia(media)
        self._one_shot_volume_adjustment = self.adjust_player_volume_by_decibel(
            self._one_shot_player, file.volume_adjustment
        )
        logger.trace(
            "Adjusted one-shot player volume by {}db", self._one_shot_volume_adjustment
        )
        self._one_shot_player.play()
        logger.trace("One-shot player playing file: {!r}", file)

    def set_player_volumes(self, volume: Number) -> None:
        volume = round(volume)
        self._loop_player.setVolume(volume)
        self._one_shot_player.setVolume(volume)

    # noinspection PyMethodMayBeStatic
    def adjust_player_volume_by_decibel(
        self, player: QMediaPlayer, decibel: Number
    ) -> Number:
        original_volume = player.volume()
        target_volume = round(add_decibel_to_linear_volume(original_volume, decibel))
        player.setVolume(target_volume)

        # Return clamped volume difference, so increasing linear volume 100 by n > 1 db
        # returns 0
        return player.volume() - original_volume

    def set_threshold(self, threshold: PlaybackThreshold) -> None:
        logger.trace("Setting channel threshold: {!r}", threshold)
        self.threshold = threshold

        if not self._loop_sound:
            return

        if self._loop_sound.playback_threshold > threshold:
            logger.trace("Stopping loop player, new threshold too low")
            self._loop_playlist.clear()
            self._loop_player.stop()
            return

        logger.trace("Loop player state: {!r}", self._loop_player.state())
        if (
            self._loop_sound.playback_threshold <= threshold
            and self._loop_player.state() == QMediaPlayer.StoppedState
        ):
            logger.trace("Replaying sound: {!r} in loop player from stopped state")
            self.play_sound(self._loop_sound)


class ChannelsWidget(QWidget):
    def __init__(self, parent: T.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ChannelsWidget()
        self.ui.setupUi(self)

        self._channels: T.Dict[T.Optional[str], Channel] = {}
        self._last_played: T.Dict[Sound, float] = collections.defaultdict(float)
        self._volume: Number = 100

    def clear(self) -> None:
        for channel in self._channels.values():
            channel.stop()

        self._channels.clear()

        while self.ui.layout.count() > 0:
            item: QLayoutItem = self.ui.layout.takeAt(0)
            widget: QWidget = item.widget()
            if widget:
                widget.deleteLater()

    def add_channel(self, name: str) -> None:
        if name in self._channels:
            return

        self._channels[name] = Channel(name, self)
        channel = QLabel(f"{name.capitalize()}:", self)
        volume = QSlider(Qt.Horizontal)
        volume.setMaximum(100)
        volume.setValue(100)

        def volume_changed() -> None:
            self.on_channel_volume_changed(name, volume.value())

        # noinspection PyUnresolvedReferences
        volume.valueChanged.connect(volume_changed)

        threshold = QComboBox(self)
        for member in PlaybackThreshold:
            threshold.addItem(member.name, member)

        # noinspection PyCallingNonCallable
        @QtCore.Slot(int)  # type: ignore
        def threshold_changed(index: int) -> None:
            self.on_channel_threshold_changed(name, index, threshold)

        # noinspection PyUnresolvedReferences
        threshold.currentIndexChanged.connect(threshold_changed)

        row = self.ui.layout.rowCount()
        self.ui.layout.setColumnStretch(1, 1)
        self.ui.layout.setColumnStretch(2, 0)
        self.ui.layout.addWidget(channel, row=row, column=0)
        self.ui.layout.addWidget(volume, row=row, column=1)
        self.ui.layout.addWidget(threshold, row=row, column=2)

    def play_sound(self, sound: Sound) -> None:
        if not sound.files:
            return

        delta = time.time() - self._last_played[sound]
        if delta < sound.delay:
            return

        roll = random.randint(0, 100)
        if sound.probability < roll:
            return

        if sound.concurrency is not None:
            playing = sum(
                1 if channel.is_playing else 0 for channel in self._channels.values()
            )
            if playing > sound.concurrency:
                return

        def play_sound() -> None:
            channel = "Default" if sound.channel is None else sound.channel
            self._channels[channel].play_sound(sound)
            self._last_played[sound] = time.time()

        QTimer.singleShot(sound.delay, play_sound)

    def set_volume(self, volume: Number) -> None:
        self._volume = volume
        factor = volume / 100
        for channel in self._channels.values():
            relative_volume = channel.slider_volume * factor
            logger.trace(
                "Adjusting channel {!r} volume to {}", channel.name, relative_volume
            )
            channel.set_player_volumes(relative_volume)

    def on_channel_volume_changed(self, channel: str, volume: int) -> None:
        linear_volume = logarithmic_to_linear_volume(volume)
        channel = self._channels[channel]
        channel.slider_volume = linear_volume

        factor = self._volume / 100
        relative_volume = linear_volume * factor
        channel.set_player_volumes(relative_volume)
        logger.trace(
            "Adjusting channel {!r} volume to {}", channel.name, relative_volume
        )

    def on_channel_threshold_changed(
        self, channel: str, index: int, sender: QComboBox
    ) -> None:
        threshold = sender.itemData(index, Qt.UserRole)
        self._channels[channel].set_threshold(threshold)
