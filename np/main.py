import asyncio
import sys
from typing import override

import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QPropertyAnimation,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QMenu,
    QSystemTrayIcon,
    QWidget,
)

from np import DEV, core, iconset, theme
from np.media import Media, PlaybackData, SessionsData, TimelineData
from np.ui.ui_main_window import Ui_MainWindow
from np.utils import log


class AppTray(QSystemTrayIcon):
    onQuit = Signal()

    def __init__(self, parent: QApplication):
        super().__init__(parent=parent)
        self.app = parent
        self.setIcon(QIcon(":/icons/play.png"))
        self.setVisible(True)
        self.mainWindow = None

        self.activated.connect(self.handleClick)

        self.menu = QMenu()
        self.showAction = self.menu.addAction("Show / Hide")
        self.showAction.triggered.connect(
            lambda: self.handleClick(QSystemTrayIcon.ActivationReason.Trigger)
        )
        self.quitAction = self.menu.addAction("Quit")
        self.quitAction.triggered.connect(lambda: self.onQuit.emit())
        self.setToolTip("Now Playing")
        self.setContextMenu(self.menu)
        self.menu.aboutToShow.connect(self.refresh_theme)
        self.refresh_theme()

        self.app.focusWindowChanged.connect(self.handleFocusChange)

        self.media = Media()
        self.media.onPlaybackInfoRefresh.connect(self.handlePlaybackInfoChange)
        self.media.onUpdateMediaSessions.connect(
            lambda _sessions: self._update_tooltip()
        )
        self.onQuit.connect(self.app.quit)
        self.app.aboutToQuit.connect(self.media.releaseAll)
        _ = asyncio.ensure_future(self.startMedia(), loop=core.loop)

    def refresh_theme(self):
        colors = theme.colors()
        self.showAction.setIcon(iconset.icon("note", colors["ACCENT"]))
        self.quitAction.setIcon(iconset.icon("close", colors["TEXT"]))

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
        self._update_tooltip()

    def _update_tooltip(self):
        apps = len(self.media.mediaSessions)
        playing = sum(
            1
            for pi in self.media.playbackInfo.values()
            if pi.playback_status == "PLAYING"
        )
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


class MainWindow(QWidget):
    WIDTH = 420
    SHOW_MARGIN = 12

    @override
    def show(self):
        """Show the popup anchored to the bottom-right of the screen."""
        self._refresh_theme()
        self._fit_to_content()
        self._position_bottom_right()
        self._dragged = False

        super().show()
        self._refresh_timelines()
        self.activateWindow()
        self.raise_()
        self._fade_in()

    def __init__(self, app: QApplication, appTray: AppTray, media: Media):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.app = app
        self.appTray = appTray
        self.media = media
        self._initialized = False
        self._dragged = False
        self._drag_offset: QPoint | None = None

        self.setWindowTitle("Now Playing")
        self.setWindowIcon(QIcon(":/icons/play.png"))
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(self.WIDTH)

        self._setup_shadow()
        self._apply_icons()
        self._setup_chrome()
        self._setup_media()
        self._update_header()
        self._fit_to_content()

    # ---------------------------------------------------------------- setup

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(theme.color("SHADOW"))
        self.ui.card.setGraphicsEffect(shadow)
        self._shadow = shadow

    def _apply_icons(self):
        colors = theme.colors()
        self.ui.logo.setPixmap(iconset.pixmap("note", colors["ACCENT"], 26))
        self.ui.closeButton.setIcon(iconset.icon("close", colors["TEXT"]))
        self.ui.loadingIcon.setPixmap(
            iconset.pixmap("note", colors["MUTED"], 46, 0.9)
        )
        self.ui.emptyIcon.setPixmap(iconset.pixmap("note", colors["FAINT"], 46, 0.8))

    def _setup_chrome(self):
        self.ui.closeButton.clicked.connect(self.hide)

        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        shortcut.activated.connect(self.hide)

        for widget in (
            self.ui.header,
            self.ui.logo,
            self.ui.appTitleLabel,
            self.ui.countLabel,
        ):
            widget.installEventFilter(self)

    def _setup_media(self):
        self.list_view = self.ui.listView
        self.list_view.onPrev.connect(
            lambda appId: asyncio.ensure_future(self.media.prev(appId))
        )
        self.list_view.onPausePlay.connect(
            lambda appId: asyncio.ensure_future(self.media.pausePlay(appId))
        )
        self.list_view.onNext.connect(
            lambda appId: asyncio.ensure_future(self.media.next(appId))
        )
        self.list_view.contentChanged.connect(self._on_content_changed)

        self.media.onPlaybackInfoRefresh.connect(self.updatePlaybackInfo)
        self.media.onUpdateMediaSessions.connect(self.updateApps)
        self.media.onMediaPropsRefresh.connect(
            lambda appId: asyncio.ensure_future(self.updateMediaInfo(appId))
        )
        self.media.onTimelineRefresh.connect(self.updateTimeline)

        self.timelineTimer = QTimer(self)
        self.timelineTimer.setInterval(1000)
        self.timelineTimer.timeout.connect(self._refresh_timelines)
        self.timelineTimer.start()

        self._initialFuture = asyncio.ensure_future(self.getInitialData(), loop=core.loop)

    # -------------------------------------------------------------- theming

    def _refresh_theme(self):
        if not theme.apply_if_needed(self.app):
            return
        self._apply_icons()
        self._shadow.setColor(theme.color("SHADOW"))
        self.list_view.refresh_theme()
        self.appTray.refresh_theme()

    # --------------------------------------------------------------- sizing

    def _content_height(self) -> int:
        current = self.ui.stack.currentWidget()
        if current is self.ui.pageList:
            return max(170, self.list_view.preferred_height())
        return 170

    def _fit_to_content(self):
        margins = self.ui.rootLayout.contentsMargins()
        card_margins = self.ui.cardLayout.contentsMargins()
        layout = self.ui.cardLayout

        chrome = (
            margins.top()
            + margins.bottom()
            + card_margins.top()
            + card_margins.bottom()
            + self.ui.header.sizeHint().height()
            + self.ui.divider.maximumHeight()
            + layout.spacing() * 2
            + 2  # card border
        )

        screen = self.screen() or QApplication.primaryScreen()
        max_height = int(screen.availableGeometry().height() * 0.78)
        height = max(250, min(chrome + self._content_height(), max_height))

        if height != self.height():
            self.setFixedSize(self.WIDTH, height)
            if self.isVisible() and not self._dragged:
                self._position_bottom_right()

    def _position_bottom_right(self):
        screen = self.screen() or QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        x = geometry.right() - self.width() - self.SHOW_MARGIN + 1
        y = geometry.bottom() - self.height() - self.SHOW_MARGIN + 1
        self.move(x, y)

    def _fade_in(self):
        self.setWindowOpacity(0.0)
        animation = QPropertyAnimation(self, b"windowOpacity", self)
        animation.setDuration(140)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self._fadeAnimation = animation

    def _on_content_changed(self):
        self._update_header()
        if self._initialized:
            self._refresh_state()

    # ---------------------------------------------------------------- state

    def _refresh_state(self):
        count = len(self.media.mediaSessions)
        if not self._initialized:
            self.ui.stack.setCurrentWidget(self.ui.pageLoading)
        elif count:
            self.ui.stack.setCurrentWidget(self.ui.pageList)
        else:
            self.ui.stack.setCurrentWidget(self.ui.pageEmpty)

        self._update_header()
        self._fit_to_content()

    def _update_header(self):
        count = len(self.media.mediaSessions)
        if not self._initialized:
            text = "Looking for media…"
        elif not count:
            text = "No active sessions"
        else:
            playing = sum(
                1
                for playback in self.media.playbackInfo.values()
                if playback.playback_status == "PLAYING"
            )
            apps = "app" if count == 1 else "apps"
            text = f"{playing} playing · {count} {apps}"
        self.ui.countLabel.setText(text)

    def updateApps(self, apps: SessionsData):
        for appId in apps.removed:
            self.list_view.removeApp(appId)
        for appId in apps.added:
            self.list_view.addApp(appId)
        self._refresh_state()

    async def getInitialData(self):
        added = [k for k in self.media.mediaSessions.keys()]
        self.updateApps(SessionsData(added=added, removed=[]))
        await asyncio.gather(*[self.updateMediaInfo(k) for k in added])
        for playback in self.media.playbackInfo.values():
            self.updatePlaybackInfo(playback)
        for appId in added:
            timeline = self.media.getTimeline(appId)
            if timeline is not None:
                self.list_view.updateTimeline(appId, timeline)
        self._initialized = True
        self._refresh_state()

    def updatePlaybackInfo(self, playback: PlaybackData):
        self.list_view.updatePlaybackInfo(playback.app, playback)
        self._update_header()

    async def updateMediaInfo(self, appId: str):
        props = await self.media.grabMediaProperties(appId)
        log.debug(f"Updating media info {props.app if props is not None else None}")
        if not props:
            return
        self.list_view.updateMediaInfo(appId, props)
        timeline = self.media.getTimeline(appId)
        if timeline is not None:
            self.list_view.updateTimeline(appId, timeline)

    def updateTimeline(self, timeline: TimelineData):
        self.list_view.updateTimeline(timeline.app, timeline)

    def _refresh_timelines(self):
        if not self.isVisible():
            return
        for appId in list(self.media.mediaSessions):
            timeline = self.media.getTimeline(appId)
            if timeline is not None:
                self.list_view.updateTimeline(appId, timeline)

    # --------------------------------------------------------------- events

    def eventFilter(self, watched, event):
        header_widgets = (
            self.ui.header,
            self.ui.logo,
            self.ui.appTitleLabel,
            self.ui.countLabel,
        )
        if watched in header_widgets:
            event_type = event.type()
            if (
                event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._drag_offset = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()
                return True
            if (
                event_type == QEvent.Type.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                self._dragged = True
                event.accept()
                return True
            if event_type == QEvent.Type.MouseButtonRelease:
                self._drag_offset = None
                event.accept()
                return True
        return super().eventFilter(watched, event)


appTray = None


async def amain(app: QApplication):
    await core.setupQLoop()
    global appTray
    appTray = AppTray(app)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Now Playing")
    app.setApplicationDisplayName("Now Playing")
    app.setOrganizationName("raffleberry")
    app.setQuitOnLastWindowClosed(False)
    theme.apply(app)

    QtAsyncio.run(amain(app), handle_sigint=True)


if __name__ == "__main__":
    main()
