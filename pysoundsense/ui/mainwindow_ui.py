# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(498, 618)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.volume_label = QLabel(self.centralwidget)
        self.volume_label.setObjectName(u"volume_label")
        self.volume_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.volume_label)

        self.volume = QSlider(self.centralwidget)
        self.volume.setObjectName(u"volume")
        self.volume.setMaximum(100)
        self.volume.setValue(100)
        self.volume.setOrientation(Qt.Horizontal)
        self.volume.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout.addWidget(self.volume)

        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        self.log_tab = QWidget()
        self.log_tab.setObjectName(u"log_tab")
        self.verticalLayout_2 = QVBoxLayout(self.log_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textEdit = QTextEdit(self.log_tab)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout_2.addWidget(self.textEdit)

        self.tabs.addTab(self.log_tab, "")
        self.playing_tab = QWidget()
        self.playing_tab.setObjectName(u"playing_tab")
        self.tabs.addTab(self.playing_tab, "")

        self.verticalLayout.addWidget(self.tabs)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 498, 28))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PySoundSense", None))
        self.volume_label.setText(QCoreApplication.translate("MainWindow", u"Volume: 100%", None))
        self.tabs.setTabText(self.tabs.indexOf(self.log_tab), QCoreApplication.translate("MainWindow", u"Logs", None))
        self.tabs.setTabText(self.tabs.indexOf(self.playing_tab), QCoreApplication.translate("MainWindow", u"Currently Playing", None))
    # retranslateUi

