"""SVG icon helpers with runtime recoloring for the active theme."""

from PySide6.QtCore import QByteArray, QFile, QIODevice, Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_icon_cache: dict[tuple[str, str, float], QIcon] = {}
_pixmap_cache: dict[tuple[str, str, int, float], QPixmap] = {}

_RENDER_SCALE = 2


def _resource_bytes(name: str) -> bytes | None:
    f = QFile(f":/icons/{name}.svg")
    if not f.open(QIODevice.OpenModeFlag.ReadOnly):
        return None
    try:
        return bytes(f.readAll().data())
    finally:
        f.close()


def _render(name: str, color: str, size: int, opacity: float) -> QPixmap:
    data = _resource_bytes(name)
    if not data:
        return QPixmap()

    renderer = QSvgRenderer(QByteArray(data))
    if not renderer.isValid():
        return QPixmap()

    device_size = max(1, int(size * _RENDER_SCALE))
    image = QImage(device_size, device_size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
    )
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.setOpacity(max(0.0, min(1.0, opacity)))
    painter.fillRect(image.rect(), QColor(color))
    painter.end()

    image.setDevicePixelRatio(_RENDER_SCALE)
    return QPixmap.fromImage(image)


def _text_color() -> str:
    # Imported lazily to avoid a circular import (theme imports iconset).
    from np import theme

    return theme.colors()["TEXT"]


def pixmap(
    name: str,
    color: str | None = None,
    size: int = 64,
    opacity: float = 1.0,
) -> QPixmap:
    """Return a themed QPixmap for a named SVG icon."""
    color = color or _text_color()
    key = (name, color.upper(), size, round(opacity, 2))
    cached = _pixmap_cache.get(key)
    if cached is None:
        cached = _render(name, color, size, opacity)
        _pixmap_cache[key] = cached
    return cached


def icon(
    name: str,
    color: str | None = None,
    size: int = 64,
    opacity: float = 1.0,
) -> QIcon:
    """Return a themed QIcon with a dimmed variant for the disabled state."""
    color = color or _text_color()
    key = (name, color.upper(), round(opacity, 2))
    cached = _icon_cache.get(key)
    if cached is not None:
        return cached

    normal = pixmap(name, color, size, opacity)
    disabled = pixmap(name, color, size, opacity * 0.32)

    result = QIcon()
    if not normal.isNull():
        result.addPixmap(normal, QIcon.Mode.Normal, QIcon.State.Off)
        result.addPixmap(normal, QIcon.Mode.Active, QIcon.State.Off)
        result.addPixmap(normal, QIcon.Mode.Selected, QIcon.State.Off)
    if not disabled.isNull():
        result.addPixmap(disabled, QIcon.Mode.Disabled, QIcon.State.Off)

    _icon_cache[key] = result
    return result


def clear_cache() -> None:
    _icon_cache.clear()
    _pixmap_cache.clear()


__all__ = ["clear_cache", "icon", "pixmap"]
