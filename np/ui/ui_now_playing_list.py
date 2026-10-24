# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'now_playing_list.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QScrollArea, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_NowPlayingList(object):
    def setupUi(self, NowPlayingList):
        if not NowPlayingList.objectName():
            NowPlayingList.setObjectName(u"NowPlayingList")
        NowPlayingList.resize(360, 400)
        NowPlayingList.setFrameShape(QFrame.Shape.NoFrame)
        NowPlayingList.setWidgetResizable(True)
        NowPlayingList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 352, 398))
        self.itemsLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.itemsLayout.setSpacing(8)
        self.itemsLayout.setObjectName(u"itemsLayout")
        self.itemsLayout.setContentsMargins(0, 0, 0, 0)
        self.itemsSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.itemsLayout.addItem(self.itemsSpacer)

        NowPlayingList.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(NowPlayingList)

        QMetaObject.connectSlotsByName(NowPlayingList)
    # setupUi

    def retranslateUi(self, NowPlayingList):
        pass
    # retranslateUi

