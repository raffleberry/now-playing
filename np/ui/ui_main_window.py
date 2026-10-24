# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
    QSizePolicy, QSpacerItem, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget)

from np.widgets.NowPlayingList import NowPlayingList

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(420, 340)
        self.rootLayout = QVBoxLayout(MainWindow)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName(u"rootLayout")
        self.rootLayout.setContentsMargins(20, 20, 20, 20)
        self.card = QFrame(MainWindow)
        self.card.setObjectName(u"card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)
        self.cardLayout = QVBoxLayout(self.card)
        self.cardLayout.setSpacing(12)
        self.cardLayout.setObjectName(u"cardLayout")
        self.cardLayout.setContentsMargins(20, 20, 20, 20)
        self.header = QWidget(self.card)
        self.header.setObjectName(u"header")
        self.headerLayout = QHBoxLayout(self.header)
        self.headerLayout.setSpacing(10)
        self.headerLayout.setObjectName(u"headerLayout")
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.logo = QLabel(self.header)
        self.logo.setObjectName(u"logo")
        self.logo.setMinimumSize(QSize(26, 26))
        self.logo.setMaximumSize(QSize(26, 26))
        self.logo.setScaledContents(True)

        self.headerLayout.addWidget(self.logo)

        self.headerTextLayout = QVBoxLayout()
        self.headerTextLayout.setSpacing(1)
        self.headerTextLayout.setObjectName(u"headerTextLayout")
        self.appTitleLabel = QLabel(self.header)
        self.appTitleLabel.setObjectName(u"appTitleLabel")

        self.headerTextLayout.addWidget(self.appTitleLabel)

        self.countLabel = QLabel(self.header)
        self.countLabel.setObjectName(u"countLabel")

        self.headerTextLayout.addWidget(self.countLabel)


        self.headerLayout.addLayout(self.headerTextLayout)

        self.headerSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerLayout.addItem(self.headerSpacer)

        self.closeButton = QToolButton(self.header)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setMinimumSize(QSize(28, 28))
        self.closeButton.setMaximumSize(QSize(28, 28))
        self.closeButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.closeButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon = QIcon()
        icon.addFile(u":/icons/close.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeButton.setIcon(icon)
        self.closeButton.setIconSize(QSize(14, 14))

        self.headerLayout.addWidget(self.closeButton)


        self.cardLayout.addWidget(self.header)

        self.divider = QFrame(self.card)
        self.divider.setObjectName(u"divider")
        self.divider.setMinimumSize(QSize(0, 1))
        self.divider.setMaximumSize(QSize(16777215, 1))
        self.divider.setFrameShape(QFrame.Shape.NoFrame)

        self.cardLayout.addWidget(self.divider)

        self.stack = QStackedWidget(self.card)
        self.stack.setObjectName(u"stack")
        self.pageLoading = QWidget()
        self.pageLoading.setObjectName(u"pageLoading")
        self.loadingLayout = QVBoxLayout(self.pageLoading)
        self.loadingLayout.setSpacing(8)
        self.loadingLayout.setObjectName(u"loadingLayout")
        self.loadingLayout.setContentsMargins(0, 0, 0, 0)
        self.loadingTopSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.loadingLayout.addItem(self.loadingTopSpacer)

        self.loadingIcon = QLabel(self.pageLoading)
        self.loadingIcon.setObjectName(u"loadingIcon")
        self.loadingIcon.setMinimumSize(QSize(46, 46))
        self.loadingIcon.setMaximumSize(QSize(46, 46))
        self.loadingIcon.setScaledContents(True)

        self.loadingLayout.addWidget(self.loadingIcon, 0, Qt.AlignmentFlag.AlignHCenter)

        self.loadingTitle = QLabel(self.pageLoading)
        self.loadingTitle.setObjectName(u"loadingTitle")
        self.loadingTitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.loadingLayout.addWidget(self.loadingTitle)

        self.loadingHint = QLabel(self.pageLoading)
        self.loadingHint.setObjectName(u"loadingHint")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadingHint.sizePolicy().hasHeightForWidth())
        self.loadingHint.setSizePolicy(sizePolicy)
        self.loadingHint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.loadingHint.setWordWrap(True)

        self.loadingLayout.addWidget(self.loadingHint)

        self.loadingBottomSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.loadingLayout.addItem(self.loadingBottomSpacer)

        self.stack.addWidget(self.pageLoading)
        self.pageList = QWidget()
        self.pageList.setObjectName(u"pageList")
        self.listPageLayout = QVBoxLayout(self.pageList)
        self.listPageLayout.setSpacing(0)
        self.listPageLayout.setObjectName(u"listPageLayout")
        self.listPageLayout.setContentsMargins(0, 0, 0, 0)
        self.listView = NowPlayingList(self.pageList)
        self.listView.setObjectName(u"listView")

        self.listPageLayout.addWidget(self.listView)

        self.stack.addWidget(self.pageList)
        self.pageEmpty = QWidget()
        self.pageEmpty.setObjectName(u"pageEmpty")
        self.emptyLayout = QVBoxLayout(self.pageEmpty)
        self.emptyLayout.setSpacing(8)
        self.emptyLayout.setObjectName(u"emptyLayout")
        self.emptyLayout.setContentsMargins(0, 0, 0, 0)
        self.emptyTopSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.emptyLayout.addItem(self.emptyTopSpacer)

        self.emptyIcon = QLabel(self.pageEmpty)
        self.emptyIcon.setObjectName(u"emptyIcon")
        self.emptyIcon.setMinimumSize(QSize(46, 46))
        self.emptyIcon.setMaximumSize(QSize(46, 46))
        self.emptyIcon.setScaledContents(True)

        self.emptyLayout.addWidget(self.emptyIcon, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emptyTitle = QLabel(self.pageEmpty)
        self.emptyTitle.setObjectName(u"emptyTitle")
        self.emptyTitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.emptyLayout.addWidget(self.emptyTitle)

        self.emptyHint = QLabel(self.pageEmpty)
        self.emptyHint.setObjectName(u"emptyHint")
        sizePolicy.setHeightForWidth(self.emptyHint.sizePolicy().hasHeightForWidth())
        self.emptyHint.setSizePolicy(sizePolicy)
        self.emptyHint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.emptyHint.setWordWrap(True)

        self.emptyLayout.addWidget(self.emptyHint)

        self.emptyBottomSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.emptyLayout.addItem(self.emptyBottomSpacer)

        self.stack.addWidget(self.pageEmpty)

        self.cardLayout.addWidget(self.stack)


        self.rootLayout.addWidget(self.card)


        self.retranslateUi(MainWindow)

        self.stack.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Now Playing", None))
        self.appTitleLabel.setText(QCoreApplication.translate("MainWindow", u"Now Playing", None))
        self.countLabel.setText(QCoreApplication.translate("MainWindow", u"Looking for media\u2026", None))
#if QT_CONFIG(tooltip)
        self.closeButton.setToolTip(QCoreApplication.translate("MainWindow", u"Hide (Esc)", None))
#endif // QT_CONFIG(tooltip)
        self.loadingTitle.setText(QCoreApplication.translate("MainWindow", u"Looking for media\u2026", None))
        self.loadingHint.setText(QCoreApplication.translate("MainWindow", u"Sessions will appear here automatically", None))
        self.emptyTitle.setText(QCoreApplication.translate("MainWindow", u"Nothing playing", None))
        self.emptyHint.setText(QCoreApplication.translate("MainWindow", u"Play something in any media app to get started", None))
    # retranslateUi

