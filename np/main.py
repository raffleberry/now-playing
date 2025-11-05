import asyncio
import sys
from typing import override

import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtCore import QRect, QSize, Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from np import DEV, core
from np.media import Media, PlaybackData, SessionsData
from np.utils import log
from np.widgets.NowPlayingList import NowPlayingList


class AppTray(QSystemTrayIcon):
    onQuit = Signal()
    def __init__(self, parent: QApplication):
        super().__init__(parent=parent)
        self.app = parent
        icon = QIcon(":/icons/play.png")
        self.setIcon(icon)
        self.setVisible(True)
        self.mainWindow = None

        self.activated.connect(self.handleClick)

        self.menu = QMenu()
        show = self.menu.addAction("Show/Hide")
        show.triggered.connect(self.handleClick)
        quit = self.menu.addAction("Quit")
        quit.triggered.connect(lambda: self.onQuit.emit())
        self.setToolTip("Now Playing")
        self.setContextMenu(self.menu)

        self.app.focusWindowChanged.connect(self.handleFocusChange)

        self.media = Media()
        self.media.onPlaybackInfoRefresh.connect(self.handlePlaybackInfoChange)
        _ = asyncio.ensure_future(self.startMedia(), loop=core.loop)

    def handleClick(self, reason: QSystemTrayIcon.ActivationReason):
        
        if reason == QSystemTrayIcon.ActivationReason.Context:
            return

        if self.mainWindow is None:
            self.mainWindow = MainWindow(self.app, self, self.media)
        
        if self.mainWindow.isVisible():
            self.mainWindow.hide()
        else:
            self.mainWindow.show()
            self.mainWindow.activateWindow()
            self.mainWindow.raise_()


    def handlePlaybackInfoChange(self, _: PlaybackData):
        apps = len(self.media.mediaSessions)
        playing = sum(1 for pi in self.media.playbackInfo.values() if pi.playback_status == "PLAYING")
        toolTipText = "Now Playing"
        if apps:
            toolTipText += f" - {playing}/{apps} apps"
        self.setToolTip(toolTipText)    
    
    def handleFocusChange(self, win):
        if DEV:
            return
        if win is None and self.mainWindow is not None:
            self.mainWindow.hide()

    async def startMedia(self):
        await self.media.start()

class MainWindow(QMainWindow):
    @override
    def show(self,):
        """set fixed width/height pls"""
        screen = QApplication.primaryScreen()
        geom: QRect = screen.availableGeometry()
        win_w, win_h = self.width(), self.height()

        x = geom.right() - win_w - 10
        y = geom.bottom() - win_h - 10
        self.move(x, y)

        super().show()
        self.activateWindow()

    @override
    def close(self,):
        super().close()

    def __init__(self, app: QApplication, appTray: AppTray, media: Media):
        super().__init__()
        self.setUpdatesEnabled(False)
        self.setFixedSize(QSize(600, 260))
        self.setUpdatesEnabled(True)

        self.app = app
        self.app.aboutToQuit.connect(self.aboutToQuit)

        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.view = QStackedWidget()
        main_layout.addWidget(self.view)

        self.loading = QLabel("Loading")
        self.view.addWidget(self.loading)

        self.list_view = NowPlayingList()
        self.list_view.onPrev.connect(lambda appId: asyncio.ensure_future(self.media.prev(appId)))
        self.list_view.onPausePlay.connect(lambda appId: asyncio.ensure_future(self.media.pausePlay(appId)))
        self.list_view.onNext.connect(lambda appId: asyncio.ensure_future(self.media.next(appId)))

        # self.list_view.doubleClicked.connect(lambda x: asyncio.ensure_future(self.handleDoubleClick(x.row())))
        self.view.addWidget(self.list_view)
        
        self.appTray = appTray
        self.appTray.onQuit.connect(self.quit)

        self.media = media

        self.media.onPlaybackInfoRefresh.connect(self.updatePlaybackInfo)
        self.media.onUpdateMediaSessions.connect(self.updateApps)
        self.media.onMediaPropsRefresh.connect(lambda appId: asyncio.ensure_future(self.updateMediaInfo(appId)))
        self._initialFuture = asyncio.ensure_future(self.getInitialData(), loop=core.loop)

    async def handleDoubleClick(self, idx):
        print(idx)


    def updateApps(self, apps: SessionsData):
        for a in apps.removed:
            self.list_view.removeApp(a)
        for a in apps.added:
            self.list_view.addApp(a)
       

    async def getInitialData(self):
        added = [k for k in self.media.mediaSessions.keys()]
        self.updateApps(SessionsData(added=added, removed=[]))
        await asyncio.gather(*[self.updateMediaInfo(k) for k in added])
        for pi in self.media.playbackInfo.values():
            self.updatePlaybackInfo(pi)
        self.view.setCurrentIndex(1)

    def updatePlaybackInfo(self, pi: PlaybackData):
        self.list_view.updatePlaybackInfo(pi.app, pi)

    async def updateMediaInfo(self, appId: str):
        props = await self.media.grabMediaProperties(appId)
        log.debug(f"Updating media info {props}")
        if not props:
            return
        self.list_view.updateMediaInfo(appId, props)

    def quit(self):
        if self.app:
            self.app.quit()

    def aboutToQuit(self):
        self.media.releaseAll()


appTray = None
async def amain(app: QApplication):
    await core.setupQLoop()
    global appTray
    appTray = AppTray(app)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    QtAsyncio.run(amain(app), handle_sigint=True)

if __name__ == "__main__":
    main()