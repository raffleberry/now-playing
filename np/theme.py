"""Application theme: Windows light/dark detection, palette and stylesheet.

The stylesheet lives in ``resources/styles/theme.qss`` and uses ``@TOKEN@``
placeholders.  Edit the colors here (or the QSS there) to retheme the app.
"""

import re
import winreg

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from np import iconset  # noqa: F401  (import registers the Qt resources)

QSS_PATH = ":/styles/theme.qss"

DARK: dict[str, str] = {
    "WINDOW": "#17171F",
    "PANEL_BORDER": "#FFFFFF14",
    "TEXT": "#F3F3F7",
    "MUTED": "#9C9CAA",
    "FAINT": "#70707E",
    "CARD": "#20202A",
    "CARD_HOVER": "#262632",
    "CARD_BORDER": "#FFFFFF0F",
    "CARD_BORDER_HOVER": "#FFFFFF24",
    "CARD_PLAYING": "#232338",
    "CARD_PLAYING_HOVER": "#282846",
    "CARD_PLAYING_BORDER": "#6C7CFF66",
    "ACCENT": "#6C7CFF",
    "ACCENT_HOVER": "#7E8CFF",
    "ACCENT_PRESSED": "#5B6BF0",
    "ACCENT_TEXT": "#FFFFFF",
    "PILL_BG": "#302F3D",
    "PILL_TEXT": "#B9B9C7",
    "TRACK": "#343442",
    "DIVIDER": "#FFFFFF0F",
    "BTN_HOVER": "#FFFFFF14",
    "BTN_PRESSED": "#FFFFFF24",
    "PLAY_DISABLED": "#3A3A4A",
    "SCROLL": "#FFFFFF24",
    "SCROLL_HOVER": "#FFFFFF42",
    "MENU_BG": "#23232D",
    "MENU_BORDER": "#FFFFFF1A",
    "MENU_SELECTED": "#6C7CFF33",
    "SHADOW": "#96000000",
}

LIGHT: dict[str, str] = {
    "WINDOW": "#F7F7FA",
    "PANEL_BORDER": "#00000012",
    "TEXT": "#17171C",
    "MUTED": "#66666F",
    "FAINT": "#8E8E98",
    "CARD": "#FFFFFF",
    "CARD_HOVER": "#FBFBFE",
    "CARD_BORDER": "#0000000F",
    "CARD_BORDER_HOVER": "#0000001F",
    "CARD_PLAYING": "#F4F6FF",
    "CARD_PLAYING_HOVER": "#EDF1FF",
    "CARD_PLAYING_BORDER": "#4F6BFF5C",
    "ACCENT": "#4F6BFF",
    "ACCENT_HOVER": "#617BFF",
    "ACCENT_PRESSED": "#3F58E0",
    "ACCENT_TEXT": "#FFFFFF",
    "PILL_BG": "#EFEFF4",
    "PILL_TEXT": "#5B5B67",
    "TRACK": "#E5E5EB",
    "DIVIDER": "#00000010",
    "BTN_HOVER": "#0000000D",
    "BTN_PRESSED": "#0000001A",
    "PLAY_DISABLED": "#C7CDEF",
    "SCROLL": "#00000024",
    "SCROLL_HOVER": "#00000040",
    "MENU_BG": "#FFFFFF",
    "MENU_BORDER": "#0000001A",
    "MENU_SELECTED": "#4F6BFF22",
    "SHADOW": "#3C000000",
}

_TOKEN_RE = re.compile(r"@([A-Z_]+)@")
_mode: str | None = None


def os_prefers_light() -> bool:
    """Return True when Windows is configured to use the light app theme."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return bool(value)
    except OSError:
        return False


def detect_mode() -> str:
    return "light" if os_prefers_light() else "dark"


def mode() -> str:
    return _mode or detect_mode()


def colors() -> dict[str, str]:
    return LIGHT if mode() == "light" else DARK


def color(name: str) -> QColor:
    return QColor(colors()[name])


def _load_qss() -> str:
    f = QFile(QSS_PATH)
    if not f.open(QIODevice.OpenModeFlag.ReadOnly):
        raise RuntimeError(f"Unable to load theme stylesheet: {QSS_PATH}")
    try:
        return bytes(f.readAll().data()).decode("utf-8")
    finally:
        f.close()


def stylesheet(for_mode: str | None = None) -> str:
    palette = LIGHT if (for_mode or mode()) == "light" else DARK
    qss = _load_qss()
    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token not in palette:
            missing.add(token)
            return match.group(0)
        return palette[token]

    qss = _TOKEN_RE.sub(replace, qss)
    if missing:
        raise KeyError(f"Missing theme color(s) in palette: {', '.join(sorted(missing))}")
    return qss


def _build_palette(palette: dict[str, str]) -> QPalette:
    p = QPalette()
    role = QPalette.ColorRole
    group = QPalette.ColorGroup

    p.setColor(role.Window, QColor(palette["WINDOW"]))
    p.setColor(role.WindowText, QColor(palette["TEXT"]))
    p.setColor(role.Base, QColor(palette["CARD"]))
    p.setColor(role.AlternateBase, QColor(palette["CARD_HOVER"]))
    p.setColor(role.Text, QColor(palette["TEXT"]))
    p.setColor(role.Button, QColor(palette["CARD"]))
    p.setColor(role.ButtonText, QColor(palette["TEXT"]))
    p.setColor(role.BrightText, QColor("#FFFFFF"))
    p.setColor(role.Highlight, QColor(palette["ACCENT"]))
    p.setColor(role.HighlightedText, QColor(palette["ACCENT_TEXT"]))
    p.setColor(role.ToolTipBase, QColor(palette["MENU_BG"]))
    p.setColor(role.ToolTipText, QColor(palette["TEXT"]))
    p.setColor(role.PlaceholderText, QColor(palette["FAINT"]))
    p.setColor(role.Mid, QColor(palette["DIVIDER"]))
    p.setColor(role.Dark, QColor(palette["PANEL_BORDER"]))
    p.setColor(role.Link, QColor(palette["ACCENT"]))

    for disabled_role in (role.WindowText, role.Text, role.ButtonText):
        p.setColor(group.Disabled, disabled_role, QColor(palette["FAINT"]))
    p.setColor(group.Disabled, role.Highlight, QColor(palette["CARD_BORDER"]))
    return p


def _app_font() -> QFont:
    font = QFont()
    font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Segoe UI Symbol"])
    font.setPointSize(10)
    return font


def apply(app: QApplication, for_mode: str | None = None) -> str:
    """Apply the theme to the whole application and return the active mode."""
    global _mode
    _mode = for_mode or detect_mode()

    app.setStyle("Fusion")
    app.setFont(_app_font())
    app.setPalette(_build_palette(colors()))
    app.setStyleSheet(stylesheet(_mode))

    iconset.clear_cache()
    return _mode


def apply_if_needed(app: QApplication) -> bool:
    """Re-apply the theme when the Windows light/dark setting changed."""
    if detect_mode() == _mode:
        return False
    apply(app)
    return True


__all__ = [
    "DARK",
    "LIGHT",
    "apply",
    "apply_if_needed",
    "color",
    "colors",
    "detect_mode",
    "mode",
    "os_prefers_light",
    "stylesheet",
]
