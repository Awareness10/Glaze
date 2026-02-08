"""Custom tab bar with rounded corners and table header styling."""

from PySide6.QtWidgets import QTabBar, QStylePainter, QStyleOptionTab, QStyle
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QPainterPath, QFont, QPen
from glaze.theme import theme


class RoundedTabBar(QTabBar):
    """Custom tab bar with rounded corners matching RoundedHeaderView style."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 8
        self._bg_color = QColor(theme.bg_primary)
        self._hover_color = QColor(theme.bg_secondary)
        self._text_color = QColor(theme.text_primary)
        self._text_secondary = QColor(theme.text_secondary)
        self._accent_color = QColor(theme.accent)
        self._hovered_tab = -1

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        self.setDrawBase(False)

        # Make background transparent for custom painting
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        # Tab styling
        self.setExpanding(False)
        self.setDocumentMode(True)

    def paintEvent(self, event):
        """Custom paint event to draw tabs with header styling."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw each tab
        for index in range(self.count()):
            self.paintTab(painter, index)

    def paintTab(self, painter: QPainter, index: int):
        """Paint individual tab with rounded corners and header styling."""
        rect = self.tabRect(index)
        is_selected = index == self.currentIndex()
        is_hovered = index == self._hovered_tab
        is_first = index == 0
        is_last = index == self.count() - 1

        painter.save()

        # Create path with rounded top corners
        path = QPainterPath()
        r = self._radius
        x, y, w, h = float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height())

        # Rounded top corners, square bottom
        path.moveTo(x, y + h)
        path.lineTo(x, y + r)
        path.arcTo(x, y, 2*r, 2*r, 180, -90)  # Top-left corner
        path.lineTo(x + w - r, y)
        path.arcTo(x + w - 2*r, y, 2*r, 2*r, 90, -90)  # Top-right corner
        path.lineTo(x + w, y + h)
        path.closeSubpath()

        # Fill background
        if is_hovered and not is_selected:
            painter.fillPath(path, QBrush(self._hover_color))
        else:
            painter.fillPath(path, QBrush(self._bg_color))

        # Draw accent line at bottom for selected tab
        if is_selected:
            painter.setPen(QPen(self._accent_color, 2))
            painter.drawLine(int(x + 4), int(y + h - 1), int(x + w - 4), int(y + h - 1))

        # Draw text
        text_color = self._text_color if is_selected else self._text_secondary
        painter.setPen(text_color)

        font = QFont()
        font.setBold(is_selected)
        font.setPointSize(10)
        if is_selected:
            font.setCapitalization(QFont.Capitalization.AllUppercase)
        painter.setFont(font)

        text = self.tabText(index)
        text_rect = rect.adjusted(12, 4, -12, -4)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.restore()

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects."""
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        self._hovered_tab = self.tabAt(pos)
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Clear hover state when mouse leaves."""
        self._hovered_tab = -1
        self.update()
        super().leaveEvent(event)

    def sizeHint(self):
        """Set tab bar height to match header height."""
        hint = super().sizeHint()
        hint.setHeight(48)
        return hint

    def tabSizeHint(self, index):
        """Set individual tab size."""
        hint = super().tabSizeHint(index)
        hint.setHeight(48)
        hint.setWidth(max(hint.width(), 120))  # Minimum tab width
        return hint
