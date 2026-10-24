"""A QLabel that ellipsizes its text to the available width."""

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget


class ElidedLabel(QLabel):
    """QLabel variant that keeps the full text but renders an elided version.

    Qt Designer drops a normal QLabel here; the full string is preserved in
    ``fullText()`` while the displayed text adapts to the label width.
    """

    def __init__(self, parent: QWidget | None = None, text: str = ""):
        super().__init__(parent)
        self._full_text = ""
        self._mode = Qt.TextElideMode.ElideRight
        self._last_elided_text = ""
        # Let layouts shrink the label; the text is elided instead of clipped.
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.setText(text)

    def minimumSizeHint(self) -> QSize:  # noqa: N802 (Qt API naming)
        hint = super().minimumSizeHint()
        return QSize(0, hint.height())

    def setText(self, text: str) -> None:  # noqa: N802 (Qt API naming)
        self._full_text = text or ""
        self._update_elided()

    def fullText(self) -> str:  # noqa: N802 (Qt API naming)
        return self._full_text

    def setElideMode(self, mode: Qt.TextElideMode) -> None:  # noqa: N802
        self._mode = mode
        self._update_elided()

    def _update_elided(self) -> None:
        width = max(0, self.contentsRect().width())
        if not width or not self._full_text:
            elided = self._full_text
        else:
            elided = self.fontMetrics().elidedText(
                self._full_text, self._mode, width
            )
        if elided != self._last_elided_text:
            self._last_elided_text = elided
            super().setText(elided)
        self.setToolTip(self._full_text if elided != self._full_text else "")

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt API naming)
        super().resizeEvent(event)
        self._update_elided()

    def changeEvent(self, event) -> None:  # noqa: N802 (Qt API naming)
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self._update_elided()


__all__ = ["ElidedLabel"]
