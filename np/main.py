import asyncio
import sys
from typing import List, override

import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtCore import QRect, QSize, Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QStackedWidget,
    QWidget

)
from PySide6.QtWidgets import QVBoxLayout
from np import core
from np.media import Media, SessionsData
from np.utils import log


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
        self.media.onUpdateMediaSessions.connect(self.handleSessionsChange)
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


    def handleSessionsChange(self, apps: SessionsData):
        active = len(self.media.mediaSessions)
        toolTipText = "Now Playing"
        if active:
            toolTipText += f" - {active} apps"
        self.setToolTip(toolTipText)    
    
    def handleFocusChange(self, win):
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

        x = geom.right() - win_w - 50
        y = geom.bottom() - win_h - 50
        self.move(x, y)

        super().show()
        self.activateWindow()

    @override
    def close(self,):
        super().close()

    def __init__(self, app: QApplication, appTray: AppTray, media: Media):
        super().__init__()
        self.setUpdatesEnabled(False)
        self.setFixedSize(QSize(320, 180))
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

        self.list_view = QListWidget()
        self.list_view_apps: List[str] = []
        self.list_view_media_info: dict[int, str] = {}
        self.view.addWidget(self.list_view)
        
        self.appTray = appTray
        self.appTray.onQuit.connect(self.quit)

        self.media = media
        self._initialFuture = asyncio.ensure_future(self.getInitialData(), loop=core.loop)

        self.media.onUpdateMediaSessions.connect(self.updateApps)
        self.media.onMediaPropsRefresh.connect(
            lambda appId: asyncio.ensure_future(self.updateMediaInfo(appId))
        )



    def getViewText(self, idx):
        if idx not in self.list_view_media_info:
            return self.list_view_apps[idx]
        return f"{self.list_view_apps[idx]}: {self.list_view_media_info[idx]}"

    def updateApps(self, apps: SessionsData):
        # remove from list view
        removedIdxs = [self.list_view_apps.index(a) for a in apps.removed]
        for a in apps.removed:
            self.list_view_apps.remove(a)
        for i in reversed(removedIdxs):
            self.list_view.takeItem(i)

        for a in apps.added:
            idx = len(self.list_view_apps)
            self.list_view_apps.append(a)
            w = QListWidgetItem(listview=self.list_view)
            w.setText(self.getViewText(idx))
            self.list_view.addItem(w)

    async def getInitialData(self):
        added = [k for k in self.media.mediaSessions.keys()]
        self.updateApps(SessionsData(added=added, removed=[]))
        await asyncio.gather(*[self.updateMediaInfo(k) for k in added])
        self.view.setCurrentIndex(1)


    async def updateMediaInfo(self, appId: str):
        props = await self.media.grabMediaProperties(appId)
        log.debug(f"Updating media info {props}")
        if not props:
            return
        for i in range(self.list_view.count()):
            if self.list_view_apps[i] == props.app:
                self.list_view_media_info[i] = (
                    f"{props.title} - {props.artist} \n{props.status}\n{props.type}"
                )
                self.list_view.item(i).setText(self.getViewText(i))
                break

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