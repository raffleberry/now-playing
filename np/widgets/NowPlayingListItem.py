import re

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from np import iconset, theme
from np.media import MediaData, PlaybackData, TimelineData
from np.ui.ui_now_playing_item import Ui_NowPlayingItem

APP_NAMES = {
    "spotify": "Spotify",
    "zune": "Media Player",
    "wmplayer": "Media Player",
    "microsoft.media": "Media Player",
    "chrome": "Chrome",
    "msedge": "Edge",
    "firefox": "Firefox",
    "opera": "Opera",
    "brave": "Brave",
    "vivaldi": "Vivaldi",
    "tidal": "TIDAL",
    "deezer": "Deezer",
    "amazon": "Amazon Music",
    "apple": "Apple Music",
    "itunes": "Apple Music",
    "vlc": "VLC",
    "foobar": "foobar2000",
    "aimp": "AIMP",
    "youtube": "YouTube Music",
    "soundcloud": "SoundCloud",
}


def app_display_name(app_id: str) -> str:
    """Turn an SMTC app id (exe name or AUMID) into something readable."""
    raw = app_id.rsplit("!", 1)[-1] if "!" in app_id else app_id
    raw = raw.replace("\\", "/").rsplit("/", 1)[-1]
    if raw.lower().endswith(".exe"):
        raw = raw[:-4]
    if "_" in raw and "." in raw:
        raw = raw.split("_", 1)[0]

    key = raw.lower()
    for needle, name in APP_NAMES.items():
        if needle in key:
            return name

    pretty = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw)
    pretty = " ".join(pretty.replace(".", " ").replace("_", " ").split())
    return pretty[:22].rstrip() or "Media"


def format_time(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class NowPlayingListItem(QWidget):
    prevClicked = Signal()
    playPauseClicked = Signal()
    nextClicked = Signal()

    ARTWORK_SIZE = 88
    ARTWORK_RADIUS = 10

    def __init__(
        self,
        app_id: str,
        artwork: bytes = b"",
        title: str = "",
        artist: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.ui = Ui_NowPlayingItem()
        self.ui.setupUi(self)

        self.app_id = app_id
        self.app_name = app_display_name(app_id)
        self._title = ""
        self._artist = ""
        self._artwork = b""
        self._playing = False
        self._position = 0.0
        self._duration = 0.0

        self.ui.appLabel.setText(self.app_name.upper())
        self.ui.appLabel.setToolTip(app_id)

        self.ui.prevButton.clicked.connect(lambda: self.prevClicked.emit())
        self.ui.playButton.clicked.connect(lambda: self.playPauseClicked.emit())
        self.ui.nextButton.clicked.connect(lambda: self.nextClicked.emit())

        self._apply_icons()
        self.set_media(title, artist, artwork)
        self.set_timeline(None, None)
        self._set_playing(False)

    # ------------------------------------------------------------------ data

    def set_media(self, title: str = "", artist: str = "", artwork: bytes = b"") -> None:
        self._title = self._clean_text(title) or "Unknown title"
        self._artist = self._clean_text(artist) or "Unknown artist"
        self._artwork = artwork or b""

        self.ui.titleLabel.setText(self._title)
        self.ui.artistLabel.setText(self._artist)
        self._update_artwork()

    def set_media_data(self, data: MediaData) -> None:
        self.set_media(data.title, data.artist, data.thumbnail)

    def set_playback(self, playback: PlaybackData) -> None:
        self.ui.prevButton.setEnabled(playback.is_previous_enabled)
        self.ui.playButton.setEnabled(playback.is_play_pause_toggle_enabled)
        self.ui.nextButton.setEnabled(playback.is_next_enabled)
        self._set_playing(playback.playback_status.upper() == "PLAYING")

    def set_timeline(
        self,
        position: float | None = None,
        duration: float | None = None,
    ) -> None:
        self._position = max(0.0, position or 0.0)
        self._duration = max(0.0, duration or 0.0)

        if duration is None:
            self.ui.progressBar.setValue(0)
            self.ui.timeLabel.setText("—")
            return

        if duration <= 0:
            # Some apps report no timeline at all, live streams report a zero end.
            self.ui.progressBar.setValue(0)
            self.ui.timeLabel.setText("LIVE" if self._position > 0 else "—")
            return

        ratio = min(1.0, self._position / duration)
        self.ui.progressBar.setValue(int(round(ratio * self.ui.progressBar.maximum())))
        self.ui.timeLabel.setText(
            f"{format_time(self._position)} / {format_time(duration)}"
        )

    def set_timeline_data(self, timeline: TimelineData) -> None:
        self.set_timeline(timeline.position, timeline.duration)

    def refresh_theme(self) -> None:
        self._apply_icons()
        self._update_artwork()
        self._set_playing(self._playing)

    # --------------------------------------------------------------- internal

    @staticmethod
    def _clean_text(text: str) -> str:
        return " ".join((text or "").split())

    def _apply_icons(self) -> None:
        palette = theme.colors()
        self.ui.prevButton.setIcon(iconset.icon("skip-back", palette["TEXT"]))
        self.ui.nextButton.setIcon(iconset.icon("skip-forward", palette["TEXT"]))
        self.ui.playButton.setIcon(
            iconset.icon(
                "pause" if self._playing else "play", palette["ACCENT_TEXT"]
            )
        )

    def _set_playing(self, playing: bool) -> None:
        changed = playing != self._playing
        self._playing = playing
        if changed:
            self._apply_icons()

        card = self.ui.sessionCard
        card.setProperty("playing", playing)
        if changed:
            card.style().unpolish(card)
            card.style().polish(card)
            card.update()

    def _update_artwork(self) -> None:
        pixmap = self._artwork_pixmap()
        if pixmap.isNull():
            return
        self.ui.artwork.setPixmap(pixmap)

    def _artwork_pixmap(self) -> QPixmap:
        size = self.ARTWORK_SIZE
        scale = 2
        raw = size * scale

        result = QPixmap(raw, raw)
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )

        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0, 0, raw, raw),
            self.ARTWORK_RADIUS * scale,
            self.ARTWORK_RADIUS * scale,
        )
        painter.setClipPath(path)

        painted = False
        if self._artwork:
            source = QPixmap()
            source.loadFromData(self._artwork)
            if not source.isNull():
                scaled = source.scaled(
                    raw,
                    raw,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = max(0, (scaled.width() - raw) // 2)
                y = max(0, (scaled.height() - raw) // 2)
                painter.drawPixmap(0, 0, scaled, x, y, raw, raw)
                painted = True

        if not painted:
            accent = QColor(theme.colors()["ACCENT"])
            if theme.mode() == "light":
                start, end = QColor("#EEF1FF"), QColor("#DCE3FF")
                note_color = accent
            else:
                start, end = accent.darker(180), accent.darker(260)
                note_color = QColor("#FFFFFF")

            gradient = QLinearGradient(0, 0, raw, raw)
            gradient.setColorAt(0.0, start)
            gradient.setColorAt(1.0, end)
            painter.fillRect(0, 0, raw, raw, gradient)

            note = iconset.pixmap("note", note_color.name(), int(size * 0.42))
            note_image = note.toImage()
            note_image.setDevicePixelRatio(1)
            painter.drawImage(
                QRectF(
                    (raw - note_image.width()) / 2,
                    (raw - note_image.height()) / 2,
                    note_image.width(),
                    note_image.height(),
                ),
                note_image,
            )

        painter.end()
        result.setDevicePixelRatio(scale)
        return result


__all__ = ["NowPlayingListItem", "app_display_name", "format_time"]
