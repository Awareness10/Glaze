"""Donate button with animated gradient border and subtle glow, active on hover."""

from PySide6.QtCore import Qt, QTimer, QRectF, QUrl
from PySide6.QtGui import (
    QPainter, QPen, QConicalGradient, QColor, QBrush,
    QPainterPath, QDesktopServices, QLinearGradient,
)
from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect

from glaze.theme import get_current_theme

PRESETS: dict[str, list[tuple[float, str]]] = {
    "rainbow": [
        (0.00, "#e94560"),
        (0.20, "#ff6b6b"),
        (0.40, "#f0a500"),
        (0.55, "#4caf50"),
        (0.70, "#64b5f6"),
        (0.85, "#ba68c8"),
        (1.00, "#e94560"),
    ],
    "gold": [
        (0.00, "#d4a017"),
        (0.12, "#f5c842"),
        (0.25, "#ffe08a"),
        (0.35, "#f0a500"),
        (0.45, "#e94560"),
        (0.55, "#ba68c8"),
        (0.65, "#64b5f6"),
        (0.75, "#4caf50"),
        (0.85, "#f5c842"),
        (1.00, "#d4a017"),
    ],
    "silver": [
        (0.00, "#7a8a9e"),
        (0.25, "#9eaab8"),
        (0.50, "#b8c4d0"),
        (0.75, "#9eaab8"),
        (1.00, "#7a8a9e"),
    ],
}

# Pure gold/silver for text — no rainbow mixing
TEXT_PRESETS: dict[str, list[tuple[float, str]]] = {
    "gold": [
        (0.00, "#d4a017"),
        (0.25, "#f5c842"),
        (0.50, "#ffe08a"),
        (0.75, "#f5c842"),
        (1.00, "#d4a017"),
    ],
    "silver": [
        (0.00, "#7a8a9e"),
        (0.25, "#9eaab8"),
        (0.50, "#b8c4d0"),
        (0.75, "#9eaab8"),
        (1.00, "#7a8a9e"),
    ],
}


class DonateButton(QPushButton):
    """Donate button with gradient border animation on hover only.

    At rest: static thin border using the preset's base color at low opacity.
    On hover: animated rotating gradient border + glow effect.

    Presets:
        - "rainbow": Full spectrum rotation
        - "gold": Warm amber shimmer
        - "silver": Cool steel shimmer
    """

    DONATE_URL = "https://ko-fi.com/awareness10"

    def __init__(self, parent=None, url: str | None = None, preset: str = "rainbow"):
        super().__init__("Donate", parent)
        if url:
            self.DONATE_URL = url

        self._preset = preset
        self._gradient_stops = PRESETS.get(preset, PRESETS["rainbow"])
        self._text_stops = TEXT_PRESETS.get(preset, self._gradient_stops)
        self._rest_color = QColor(self._gradient_stops[0][1])
        self._rest_color.setAlpha(80)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setMinimumWidth(100)

        self._angle = 0.0
        self._hovered = False
        self._border_width = 1.5
        self._radius = 8.0

        # Animation timer — only runs while hovered
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

        # Glow effect — hidden at rest
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setBlurRadius(0)
        self._glow.setOffset(0, 0)
        self._glow.setColor(QColor(self._gradient_stops[0][1]))
        self.setGraphicsEffect(self._glow)

        self.clicked.connect(self._open_url)

    def _rotate(self):
        self._angle = (self._angle + 1.0) % 360.0

        idx = self._angle / 360.0
        for i in range(len(self._gradient_stops) - 1):
            pos_a, col_a = self._gradient_stops[i]
            pos_b, _ = self._gradient_stops[i + 1]
            if pos_a <= idx <= pos_b:
                self._glow.setColor(QColor(col_a))
                break

        self._glow.setBlurRadius(16)
        self.update()

    def _open_url(self):
        QDesktopServices.openUrl(QUrl(self.DONATE_URL))

    def enterEvent(self, event):
        self._hovered = True
        self._timer.start(33)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._timer.stop()
        self._glow.setBlurRadius(0)
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        t = get_current_theme()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bw = self._border_width
        r = self._radius
        rect = QRectF(bw / 2, bw / 2, self.width() - bw, self.height() - bw)

        # --- Background fill ---
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect, r, r)
        painter.fillPath(bg_path, QBrush(QColor(t.bg_secondary)))

        # --- Border ---
        if self._hovered:
            gradient = QConicalGradient(rect.center(), self._angle)
            for pos, color in self._gradient_stops:
                gradient.setColorAt(pos, QColor(color))
            pen = QPen(QBrush(gradient), bw)
        else:
            pen = QPen(self._rest_color, bw)

        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, r, r)

        # --- Text ---
        font = painter.font()
        font.setPixelSize(13)
        font.setWeight(font.Weight.Medium)
        painter.setFont(font)

        is_light = QColor(t.bg_primary).lightnessF() > 0.4

        if self._hovered:
            if is_light:
                # Solid color from preset base — readable on light backgrounds
                painter.setPen(QColor(self._gradient_stops[0][1]))
            else:
                # Gradient text on dark backgrounds
                text_gradient = QConicalGradient(rect.center(), self._angle)
                for pos, color in self._text_stops:
                    text_gradient.setColorAt(pos, QColor(color))
                painter.setPen(QPen(QBrush(text_gradient), 0))
        else:
            painter.setPen(QColor(t.text_primary))

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

        painter.end()
