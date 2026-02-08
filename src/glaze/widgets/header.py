from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QPainterPath, QFont
from glaze.theme import get_current_theme


class RoundedHeaderView(QHeaderView):
    """Custom header view with rounded corners on first/last sections."""

    def __init__(self, orientation: Qt.Orientation, parent=None):
        super().__init__(orientation, parent)
        self.setFixedHeight(48)
        self._radius = 12  # Match container's border-radius
        self._hovered_section = -1
        self.setMouseTracking(True)

        # Initialize colors from current theme
        self._update_theme_colors()

        # Critical: Make header and viewport transparent so custom painting shows
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        if self.viewport():
            self.viewport().setAutoFillBackground(False) # type: ignore
            self.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # type: ignore

    def _update_theme_colors(self):
        """Update colors from current theme."""
        theme = get_current_theme()
        self._bg_color = QColor(theme.bg_primary)
        self._hover_color = QColor(theme.bg_secondary)
        self._text_color = QColor(theme.text_primary)
        self._accent_color = QColor(theme.accent)

    def refresh_theme(self):
        """Refresh colors from current theme and repaint."""
        self._update_theme_colors()
        self.viewport().update() if self.viewport() else None
    
    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:
        if not painter:
            return
            
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_first = logical_index == 0
        is_last = logical_index == self.count() - 1
        is_hovered = logical_index == self._hovered_section
        
        path = QPainterPath()
        r = self._radius
        x, y, w, h = float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height())
        
        if is_first and is_last:
            # Single column: both top corners rounded
            path.moveTo(x + r, y)
            path.lineTo(x + w - r, y)
            path.arcTo(x + w - 2*r, y, 2*r, 2*r, 90, -90)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + r)
            path.arcTo(x, y, 2*r, 2*r, 180, -90)
            path.closeSubpath()
        elif is_first:
            # First column: top-left rounded
            path.moveTo(x + r, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + r)
            path.arcTo(x, y, 2*r, 2*r, 180, -90)
            path.closeSubpath()
        elif is_last:
            # Last column: top-right rounded
            path.moveTo(x, y)
            path.lineTo(x + w - r, y)
            path.arcTo(x + w - 2*r, y, 2*r, 2*r, 90, -90)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.closeSubpath()
        else:
            # Middle columns: no rounding
            path.addRect(x, y, w, h)
        
        # Fill background
        bg = self._hover_color if is_hovered else self._bg_color
        painter.fillPath(path, QBrush(bg))
        
        # Draw accent line at bottom
        painter.setPen(self._accent_color)
        painter.drawLine(int(x), int(y + h - 1), int(x + w), int(y + h - 1))
        
        # Draw text
        painter.setPen(self._text_color)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        font.setCapitalization(QFont.Capitalization.AllUppercase)
        painter.setFont(font)
        
        text = self.model().headerData(logical_index, self.orientation(), Qt.ItemDataRole.DisplayRole) # type: ignore
        text_rect = rect.adjusted(12, 0, -12, -2)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(text))
        
        painter.restore()
    
    def mouseMoveEvent(self, event):
        pos = event.position().toPoint() if hasattr(event, 'position') else event.pos()
        self._hovered_section = self.logicalIndexAt(pos)
        self.viewport().update() # type: ignore
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        self._hovered_section = -1
        self.viewport().update() # type: ignore
        super().leaveEvent(event)