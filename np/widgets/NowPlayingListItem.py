import sys

from PySide6.QtGui import QFontMetrics, QPixmap, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QIcon


class NowPlayingListItem(QWidget):
    iconPlay = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart)
    iconPause = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause)
    iconNext = QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipForward)
    iconPrev = QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipBackward)

    def __init__(self, app_exe, artwork_path="", title="", artist=""):
        super().__init__()


        # ==== Artwork (Left Column) ====
        self.artwork_label = QLabel()
        pixmap = QPixmap(artwork_path)
        if pixmap.isNull():
            pixmap = QPixmap(120, 120)
            pixmap.fill(Qt.GlobalColor.darkGray)
        self.artwork_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.artwork_label.setFixedSize(120, 120)

        # ==== Right Column ====
        # Top Row: Title + Artist + Application
        self.title_label = QLabel()
        self.artist_label = QLabel(artist)
        self.artist_label.setStyleSheet("color: gray; font-size: 12px;")

        # Ellipsize title name
        font_metrics = QFontMetrics(self.title_label.font())
        elided_text = font_metrics.elidedText(title, Qt.TextElideMode.ElideRight, 400)
        self.title_label.setText(elided_text)
        self.title_label.setStyleSheet("font-size: 14px;")

        self.app_exe_label = QLabel()
        self.app_exe_label.setText(f"{app_exe}")
        self.app_exe_label.setStyleSheet("color: gray; font-size: 12px;")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.artist_label)
        text_layout.addWidget(self.app_exe_label)

        # Bottom Row: Control Buttons
        self.prev_button = QPushButton(self.iconPrev, "")
        self.play_button = QPushButton(self.iconPause, "")
        self.next_button = QPushButton(self.iconNext, "")        # self.vol_button = QSlider(Qt.Orientation.Horizontal)

        for b in [self.prev_button, self.play_button, self.next_button]:
            b.setFixedSize(40, 40)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Stack text + controls vertically
        right_layout = QVBoxLayout()
        right_layout.addLayout(text_layout)
        right_layout.addLayout(control_layout)
        right_layout.setContentsMargins(10, 5, 10, 5)

        # Combine Artwork + Right Side
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.artwork_label)
        main_layout.addLayout(right_layout)
        main_layout.addStretch()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)





class _MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music List Example")

        self.view = QVBoxLayout(self)
        self.view.addWidget(NowPlayingListItem("app1.exe", "artwork.jpg", "Long Track Name Example That Should Ellipsize", "Artist One"))

        self.setLayout(self.view)
        self.resize(640, 480)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = _MainWindow()
    w.show()
    sys.exit(app.exec())
