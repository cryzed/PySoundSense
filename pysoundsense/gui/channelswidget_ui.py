# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'channelswidget.ui'
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


class Ui_ChannelsWidget(object):
    def setupUi(self, ChannelsWidget):
        if not ChannelsWidget.objectName():
            ChannelsWidget.setObjectName(u"ChannelsWidget")
        ChannelsWidget.resize(353, 258)
        self.verticalLayout = QVBoxLayout(ChannelsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.layout = QGridLayout()
        self.layout.setObjectName(u"layout")

        self.verticalLayout.addLayout(self.layout)

        self.verticalSpacer = QSpacerItem(20, 235, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(ChannelsWidget)
    # setupUi

    def retranslateUi(self, ChannelsWidget):
        ChannelsWidget.setWindowTitle(QCoreApplication.translate("ChannelsWidget", u"Form", None))
    # retranslateUi

