import typing as T

from PySide2.QtCore import QObject, Qt, Signal
from PySide2.QtWidgets import QWidget, QLabel, QSlider, QLayoutItem

from .channelswidget_ui import Ui_ChannelsWidget


class ChannelsWidget(QWidget):
    volume_changed = Signal(str, int)

    def __init__(self, parent: T.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ChannelsWidget()
        self.ui.setupUi(self)

    def add_channel(self, name: str) -> None:
        label = QLabel(f"{name.capitalize()}:", self)
        slider = QSlider(Qt.Horizontal)
        slider.setMaximum(100)
        slider.setValue(100)
        slider.valueChanged.connect(
            lambda: self.volume_changed.emit(name, slider.value())
        )

        count = self.ui.layout.rowCount()
        self.ui.layout.setColumnStretch(1, 1)
        self.ui.layout.addWidget(label, row=count, column=0)
        self.ui.layout.addWidget(slider, row=count, column=1)

    def clear(self) -> None:
        while self.ui.layout.count() > 0:
            item: QLayoutItem = self.ui.layout.takeAt(0)
            widget: QWidget = item.widget()
            if widget:
                widget.deleteLater()
