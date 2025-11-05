import enum
from typing import List
from PySide6.QtWidgets import QListWidget
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from np.media import MediaData, PlaybackData, SessionsData
from np.widgets.NowPlayingListItem import NowPlayingListItem
from PySide6.QtWidgets import QApplication
import sys
from PySide6.QtWidgets import QScrollArea
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame

class NowPlayingList(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        self.view = QFrame(self)
        self.viewLayout = QVBoxLayout(self.view)
        self.setWidget(self.view)
        self.viewApps: List[str] = []
        self.viewWidgets: List[NowPlayingListItem] = []
        self.playbackInfo: dict[str, PlaybackData] = {}
        self.mediaInfo: dict[str, MediaData] = {}

    def removeApp(self, appId: str):
        print(self.size(), self.viewLayout.sizeHint())
        idx = self.viewApps.index(appId)
        self.viewApps.pop(idx)
        w = self.viewWidgets.pop(idx)
        self.viewLayout.removeWidget(w)
        self.mediaInfo.pop(appId)
        self.playbackInfo.pop(appId)

        w.deleteLater()
        # self.viewLayout.update()
        # self.view.adjustSize()
        # self.view.update()
        # self.viewport().update()

    def addApp(self, appId: str):
        self.viewApps.append(appId)

        title = ""
        artist = ""
        m = self.mediaInfo.get(appId, None)
        if m:
            title = m.title
            artist = m.artist
        w = NowPlayingListItem(app_exe=appId, title=title, artist=artist)

        p = self.playbackInfo.get(appId, None)
        if p:
            w.next_button.setEnabled(p.is_next_enabled)
            w.prev_button.setEnabled(p.is_previous_enabled)
            w.play_button.setEnabled(p.is_play_pause_toggle_enabled)
            w.play_button.setIcon(w.iconPlay if p.playback_status == "PAUSED" else w.iconPause)

        self.viewLayout.addWidget(w)
        self.viewWidgets.append(w)

    def updatePlaybackInfo(self, appId: str, p: PlaybackData):
        self.playbackInfo[appId] = p
        for i, app in enumerate(self.viewApps):
            if app == appId:
                item = self.viewWidgets[i]
                item.next_button.setEnabled(p.is_next_enabled)
                item.prev_button.setEnabled(p.is_previous_enabled)
                item.play_button.setEnabled(p.is_play_pause_toggle_enabled)
                item.play_button.setIcon(item.iconPlay if p.playback_status == "PAUSED" else item.iconPause)

    def updateMediaInfo(self, appId: str, m: MediaData):
        self.mediaInfo[appId] = m
        for i, app in enumerate(self.viewApps):
            if app == appId:
                item = self.viewWidgets[i]
                item.title_label.setText(m.title)
                item.artist_label.setText(m.artist)

if __name__ == "__main__":
    class _MainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Now Playing Example")
            self.list_widget = NowPlayingList()
            self.list_widget.addApp("app1.exe")
            self.list_widget.updateMediaInfo(
                "app1.exe",
                MediaData(app="app1.exe", title="Long Track Name Example That Should Ellipsize", artist="Artist One")
            )

            self.list_widget.addApp("app2.exe")
            self.list_widget.updateMediaInfo(
                "app2.exe",
                MediaData(app="app2.exe", title="Long Track Name Example That Should Ellipsize", artist="Artist One")
            )


            self.list_widget.addApp("app3.exe")
            self.list_widget.updateMediaInfo(
                "app3.exe",
                MediaData(app="app3.exe", title="Long Track Name Example That Should Ellipsize", artist="Artist One")
            )
            layout = QVBoxLayout(self)
            layout.addWidget(self.list_widget)
            self.setLayout(layout)
            self.resize(640, 360)

    app = QApplication(sys.argv)
    w = _MainWindow()
    w.show()
    sys.exit(app.exec())