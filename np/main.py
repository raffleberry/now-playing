import asyncio
import sys
from typing import List

import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
)
from PySide6.QtWidgets import QListWidgetItem
import np.icons  # noqa: F401
from np.utils import log
from np.media import Media, SessionsData


class AppTray(QSystemTrayIcon):
    onQuit = Signal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        icon = QIcon(":/icons/play.png")
        self.setIcon(icon)
        self.setVisible(True)

        self.menu = QMenu()
        show = self.menu.addAction("Show/Hide")
        show.triggered.connect(
            lambda: self.activated.emit(QSystemTrayIcon.ActivationReason.Trigger)
        )

        quit = self.menu.addAction("Quit")
        quit.triggered.connect(self.onQuit)

        self.setToolTip("Now Playing")
        self.setContextMenu(self.menu)


class MainWindow(QMainWindow):
    def __init__(self, media: Media, app: QApplication):
        super().__init__()

        self.app = app
        self.app.aboutToQuit.connect(self.aboutToQuit)

        self.list_view = QListWidget()
        self.list_view.hide()
        self.list_view_apps: List[str] = []
        self.list_view_media_info: dict[int, str] = {}
        self.loading = QLabel("Loading...")
        self.setCentralWidget(self.loading)

        self.appTray = AppTray(self)
        self.appTray.onQuit.connect(self.quit)
        self.appTray.activated.connect(self.handleTrayActions)

        self.media = media
        self.media.onUpdateMediaSessions.connect(self.update_apps)
        self.media.onMediaPropsRefresh.connect(
            lambda appId: asyncio.ensure_future(self.update_media_info(appId))
        )
        _ = asyncio.ensure_future(self.startMedia(), loop=self.media.loop)

    async def startMedia(self):
        await self.media.start()
        self.loading.hide()
        self.list_view.show()
        self.setCentralWidget(self.list_view)

    def get_view_text(self, idx):
        if idx not in self.list_view_media_info:
            return self.list_view_apps[idx]
        return f"{self.list_view_apps[idx]}: {self.list_view_media_info[idx]}"

    def update_apps(self, apps: SessionsData):
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
            w.setText(self.get_view_text(idx))
            self.list_view.addItem(w)

    async def update_media_info(self, appId: str):
        props = await self.media.grabMediaProperties(appId)
        log.debug(f"Updating media info {props}")
        if not props:
            return
        for i in range(self.list_view.count()):
            if self.list_view_apps[i] == props.app:
                self.list_view_media_info[i] = (
                    f"{props.title} - {props.artist} | {props.status} | {props.type}"
                )
                self.list_view.item(i).setText(self.get_view_text(i))
                break

    def quit(self):
        if self.app:
            self.app.quit()

    def aboutToQuit(self):
        self.media.releaseAll()

    def handleTrayActions(self):
        if self.isHidden():
            self.show()
        else:
            self.activateWindow()


main_window = None


async def main():
    global main_window
    media = Media()
    await media.registerLoop()
    main_window = MainWindow(media, app)
    main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    QtAsyncio.run(main(), handle_sigint=True)
