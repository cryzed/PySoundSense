import typing as T

from PySide2.QtWidgets import QMainWindow

from .mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(
        self, game_log_path: T.Optional[str] = None, pack_path: T.Optional[str] = None,
    ):
        super().__init__()
        self.game_log_path = game_log_path
        self.pack_path = pack_path

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
