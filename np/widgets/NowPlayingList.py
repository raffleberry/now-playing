import sys
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from np.media import MediaData, PlaybackData, TimelineData
from np.ui.ui_now_playing_list import Ui_NowPlayingList
from np.widgets.NowPlayingListItem import NowPlayingListItem


class NowPlayingList(QScrollArea):
    onPrev = Signal(str)
    onPausePlay = Signal(str)
    onNext = Signal(str)
    contentChanged = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_NowPlayingList()
        self.ui.setupUi(self)

        self.viewApps: List[str] = []
        self.viewWidgets: List[NowPlayingListItem] = []
        self.playbackInfo: dict[str, PlaybackData] = {}
        self.mediaInfo: dict[str, MediaData] = {}
        self.timelineInfo: dict[str, TimelineData] = {}

    # ---------------------------------------------------------------- apps

    def removeApp(self, appId: str):
        if appId not in self.viewApps:
            return

        idx = self.viewApps.index(appId)
        self.viewApps.pop(idx)
        widget = self.viewWidgets.pop(idx)
        self.ui.itemsLayout.removeWidget(widget)
        self.mediaInfo.pop(appId, None)
        self.playbackInfo.pop(appId, None)
        self.timelineInfo.pop(appId, None)
        widget.deleteLater()

        self.contentChanged.emit()

    def addApp(self, appId: str):
        if appId in self.viewApps:
            return

        widget = NowPlayingListItem(app_id=appId)
        widget.prevClicked.connect(lambda app_id=appId: self.onPrev.emit(app_id))
        widget.playPauseClicked.connect(
            lambda app_id=appId: self.onPausePlay.emit(app_id)
        )
        widget.nextClicked.connect(lambda app_id=appId: self.onNext.emit(app_id))

        media = self.mediaInfo.get(appId)
        if media:
            widget.set_media_data(media)

        playback = self.playbackInfo.get(appId)
        if playback:
            widget.set_playback(playback)

        timeline = self.timelineInfo.get(appId)
        if timeline:
            widget.set_timeline_data(timeline)

        # Keep the expanding spacer at the end of the layout.
        self.ui.itemsLayout.insertWidget(self.ui.itemsLayout.count() - 1, widget)
        self.viewApps.append(appId)
        self.viewWidgets.append(widget)

        self.contentChanged.emit()

    # ---------------------------------------------------------------- data

    def updatePlaybackInfo(self, appId: str, playback: PlaybackData):
        self.playbackInfo[appId] = playback
        widget = self._widgetFor(appId)
        if widget:
            widget.set_playback(playback)

    def updateMediaInfo(self, appId: str, media: MediaData):
        self.mediaInfo[appId] = media
        widget = self._widgetFor(appId)
        if widget:
            widget.set_media_data(media)

    def updateTimeline(self, appId: str, timeline: TimelineData | None):
        if timeline is None:
            self.timelineInfo.pop(appId, None)
        else:
            self.timelineInfo[appId] = timeline

        widget = self._widgetFor(appId)
        if widget:
            if timeline is None:
                widget.set_timeline(None, None)
            else:
                widget.set_timeline_data(timeline)

    # --------------------------------------------------------------- layout

    def preferred_height(self) -> int:
        """Height needed to show every card without scrolling."""
        if not self.viewWidgets:
            return 0

        layout = self.ui.itemsLayout
        margins = layout.contentsMargins()
        heights = [widget.sizeHint().height() for widget in self.viewWidgets]
        return (
            margins.top()
            + margins.bottom()
            + sum(heights)
            + layout.spacing() * max(0, len(heights) - 1)
        )

    def refresh_theme(self):
        for widget in self.viewWidgets:
            widget.refresh_theme()

    def _widgetFor(self, appId: str) -> NowPlayingListItem | None:
        try:
            return self.viewWidgets[self.viewApps.index(appId)]
        except ValueError:
            return None


if __name__ == "__main__":
    from np import theme

    def _demo():
        app = QApplication(sys.argv)
        theme.apply(app)

        host = QFrame()
        host.setObjectName("card")
        host.setWindowTitle("Now Playing - list preview")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(16, 16, 16, 16)

        list_widget = NowPlayingList()
        layout.addWidget(list_widget)

        demo = [
            (
                "Spotify.exe",
                "A Very Long Track Name That Should Ellipsize Gracefully",
                "Some Artist",
                "PLAYING",
                83,
                245,
            ),
            (
                "chrome.exe",
                "Another Song",
                "Another Artist",
                "PAUSED",
                12,
                201,
            ),
            (
                "Microsoft.ZuneMusic_8wekyb3d8bbwe!Microsoft.ZuneMusic",
                "Live Radio Session",
                "Various Artists",
                "PLAYING",
                0,
                0,
            ),
        ]
        for app_id, title, artist, status, position, duration in demo:
            list_widget.addApp(app_id)
            list_widget.updateMediaInfo(
                app_id,
                MediaData(app=app_id, title=title, artist=artist, thumbnail=b""),
            )
            list_widget.updatePlaybackInfo(
                app_id,
                PlaybackData(
                    app=app_id,
                    playback_status=status,
                    is_play_pause_toggle_enabled=True,
                    is_next_enabled=True,
                    is_previous_enabled=True,
                ),
            )
            list_widget.updateTimeline(
                app_id,
                TimelineData(app=app_id, position=position, duration=duration),
            )

        host.resize(400, 520)
        host.show()
        sys.exit(app.exec())

    _demo()
