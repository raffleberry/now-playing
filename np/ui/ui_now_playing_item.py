# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'now_playing_item.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from np.widgets.ElidedLabel import ElidedLabel

class Ui_NowPlayingItem(object):
    def setupUi(self, NowPlayingItem):
        if not NowPlayingItem.objectName():
            NowPlayingItem.setObjectName(u"NowPlayingItem")
        NowPlayingItem.resize(360, 140)
        self.outerLayout = QVBoxLayout(NowPlayingItem)
        self.outerLayout.setSpacing(0)
        self.outerLayout.setObjectName(u"outerLayout")
        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.sessionCard = QFrame(NowPlayingItem)
        self.sessionCard.setObjectName(u"sessionCard")
        self.sessionCard.setFrameShape(QFrame.Shape.NoFrame)
        self.cardLayout = QVBoxLayout(self.sessionCard)
        self.cardLayout.setSpacing(10)
        self.cardLayout.setObjectName(u"cardLayout")
        self.cardLayout.setContentsMargins(12, 12, 12, 12)
        self.contentLayout = QHBoxLayout()
        self.contentLayout.setSpacing(12)
        self.contentLayout.setObjectName(u"contentLayout")
        self.artwork = QLabel(self.sessionCard)
        self.artwork.setObjectName(u"artwork")
        self.artwork.setMinimumSize(QSize(88, 88))
        self.artwork.setMaximumSize(QSize(88, 88))

        self.contentLayout.addWidget(self.artwork)

        self.infoLayout = QVBoxLayout()
        self.infoLayout.setSpacing(2)
        self.infoLayout.setObjectName(u"infoLayout")
        self.metaLayout = QHBoxLayout()
        self.metaLayout.setSpacing(6)
        self.metaLayout.setObjectName(u"metaLayout")
        self.appLabel = QLabel(self.sessionCard)
        self.appLabel.setObjectName(u"appLabel")

        self.metaLayout.addWidget(self.appLabel)

        self.metaSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.metaLayout.addItem(self.metaSpacer)


        self.infoLayout.addLayout(self.metaLayout)

        self.titleLabel = ElidedLabel(self.sessionCard)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setMinimumSize(QSize(0, 19))

        self.infoLayout.addWidget(self.titleLabel)

        self.artistLabel = ElidedLabel(self.sessionCard)
        self.artistLabel.setObjectName(u"artistLabel")
        self.artistLabel.setMinimumSize(QSize(0, 16))

        self.infoLayout.addWidget(self.artistLabel)

        self.infoSpacer = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.infoLayout.addItem(self.infoSpacer)

        self.controlsLayout = QHBoxLayout()
        self.controlsLayout.setSpacing(4)
        self.controlsLayout.setObjectName(u"controlsLayout")
        self.prevButton = QPushButton(self.sessionCard)
        self.prevButton.setObjectName(u"prevButton")
        self.prevButton.setMinimumSize(QSize(30, 30))
        self.prevButton.setMaximumSize(QSize(30, 30))
        self.prevButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prevButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon = QIcon()
        icon.addFile(u":/icons/skip-back.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.prevButton.setIcon(icon)
        self.prevButton.setIconSize(QSize(15, 15))
        self.prevButton.setFlat(True)

        self.controlsLayout.addWidget(self.prevButton)

        self.playButton = QPushButton(self.sessionCard)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setMinimumSize(QSize(38, 38))
        self.playButton.setMaximumSize(QSize(38, 38))
        self.playButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.playButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon1 = QIcon()
        icon1.addFile(u":/icons/pause.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.playButton.setIcon(icon1)
        self.playButton.setIconSize(QSize(16, 16))
        self.playButton.setFlat(True)

        self.controlsLayout.addWidget(self.playButton)

        self.nextButton = QPushButton(self.sessionCard)
        self.nextButton.setObjectName(u"nextButton")
        self.nextButton.setMinimumSize(QSize(30, 30))
        self.nextButton.setMaximumSize(QSize(30, 30))
        self.nextButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.nextButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon2 = QIcon()
        icon2.addFile(u":/icons/skip-forward.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.nextButton.setIcon(icon2)
        self.nextButton.setIconSize(QSize(15, 15))
        self.nextButton.setFlat(True)

        self.controlsLayout.addWidget(self.nextButton)

        self.controlsSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.controlsLayout.addItem(self.controlsSpacer)


        self.infoLayout.addLayout(self.controlsLayout)


        self.contentLayout.addLayout(self.infoLayout)


        self.cardLayout.addLayout(self.contentLayout)

        self.progressLayout = QHBoxLayout()
        self.progressLayout.setSpacing(8)
        self.progressLayout.setObjectName(u"progressLayout")
        self.progressBar = QProgressBar(self.sessionCard)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(0, 4))
        self.progressBar.setMaximumSize(QSize(16777215, 4))
        self.progressBar.setMaximum(1000)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)

        self.progressLayout.addWidget(self.progressBar)

        self.timeLabel = QLabel(self.sessionCard)
        self.timeLabel.setObjectName(u"timeLabel")
        self.timeLabel.setMinimumSize(QSize(78, 12))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeLabel.sizePolicy().hasHeightForWidth())
        self.timeLabel.setSizePolicy(sizePolicy)
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.progressLayout.addWidget(self.timeLabel)


        self.cardLayout.addLayout(self.progressLayout)


        self.outerLayout.addWidget(self.sessionCard)


        self.retranslateUi(NowPlayingItem)

        QMetaObject.connectSlotsByName(NowPlayingItem)
    # setupUi

    def retranslateUi(self, NowPlayingItem):
        self.appLabel.setText(QCoreApplication.translate("NowPlayingItem", u"APP", None))
        self.titleLabel.setText(QCoreApplication.translate("NowPlayingItem", u"Title", None))
        self.artistLabel.setText(QCoreApplication.translate("NowPlayingItem", u"Artist", None))
#if QT_CONFIG(tooltip)
        self.prevButton.setToolTip(QCoreApplication.translate("NowPlayingItem", u"Previous", None))
#endif // QT_CONFIG(tooltip)
        self.prevButton.setText("")
#if QT_CONFIG(tooltip)
        self.playButton.setToolTip(QCoreApplication.translate("NowPlayingItem", u"Play / Pause", None))
#endif // QT_CONFIG(tooltip)
        self.playButton.setText("")
#if QT_CONFIG(tooltip)
        self.nextButton.setToolTip(QCoreApplication.translate("NowPlayingItem", u"Next", None))
#endif // QT_CONFIG(tooltip)
        self.nextButton.setText("")
        self.timeLabel.setText("")
        pass
    # retranslateUi

