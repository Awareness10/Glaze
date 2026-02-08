"""Custom title bar widget for frameless windows with themed decorations.

This module provides a custom title bar that replaces the default window
decorations with a dark-themed alternative matching the application style.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QColor

from ..theme import get_current_theme
from ..wayland import is_wayland

# Button size constant
BUTTON_SIZE = 36
# Resize margin for top edge detection in title bar
RESIZE_MARGIN = 6


class TitleBarButton(QPushButton):
    """Base styled button for title bar controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_base_style()

    def _apply_base_style(self):
        t = get_current_theme()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {t.surface_variant};
            }}
            QPushButton:pressed {{
                background-color: {t.bg_tertiary};
            }}
        """)


class MinimizeButton(TitleBarButton):
    """Minimize button with underscore icon."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        super().paintEvent(event)
        t = get_current_theme()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(t.text_secondary))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        line_width = 12
        y = h // 2 + 5
        x1 = (w - line_width) // 2
        x2 = x1 + line_width

        painter.drawLine(x1, y, x2, y)


class MaximizeButton(TitleBarButton):
    """Maximize button with diagonal double-arrow icon (COSMIC style)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_maximized = False

    def set_maximized(self, maximized: bool):
        self._is_maximized = maximized
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        t = get_current_theme()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(t.text_secondary))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        if self._is_maximized:
            size = 4
            offset = 5
            painter.drawLine(cx + offset, cy - offset, cx + offset - size, cy - offset + size)
            painter.drawLine(cx + offset, cy - offset, cx + offset - size, cy - offset)
            painter.drawLine(cx + offset, cy - offset, cx + offset, cy - offset + size)
            painter.drawLine(cx - offset, cy + offset, cx - offset + size, cy + offset - size)
            painter.drawLine(cx - offset, cy + offset, cx - offset + size, cy + offset)
            painter.drawLine(cx - offset, cy + offset, cx - offset, cy + offset - size)
        else:
            size = 4
            offset = 5
            painter.drawLine(cx + offset - size, cy - offset + size, cx + offset, cy - offset)
            painter.drawLine(cx + offset, cy - offset, cx + offset - size, cy - offset)
            painter.drawLine(cx + offset, cy - offset, cx + offset, cy - offset + size)
            painter.drawLine(cx - offset + size, cy + offset - size, cx - offset, cy + offset)
            painter.drawLine(cx - offset, cy + offset, cx - offset + size, cy + offset)
            painter.drawLine(cx - offset, cy + offset, cx - offset, cy + offset - size)


class CloseButton(TitleBarButton):
    """Close button with X icon and red hover effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovered = False

    def _apply_base_style(self):
        t = get_current_theme()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {t.danger};
            }}
            QPushButton:pressed {{
                background-color: {t.danger};
            }}
        """)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        t = get_current_theme()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("white") if self._hovered else QColor(t.text_secondary)
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        size = 5
        cx, cy = w // 2, h // 2

        painter.drawLine(cx - size, cy - size, cx + size, cy + size)
        painter.drawLine(cx + size, cy - size, cx - size, cy + size)


class TitleBar(QWidget):
    """Custom title bar widget with drag support and window controls."""

    # Interaction modes
    MODE_NONE = 0
    MODE_DRAG = 1
    MODE_RESIZE = 2

    def __init__(self, window: QWidget, title: str = "", show_icon: bool = True):
        super().__init__()
        self.window = window
        self._mode = self.MODE_NONE
        self._drag_start_pos: QPoint | None = None
        self._drag_start_window_pos: QPoint | None = None
        self._resize_edge: str = ""
        self._resize_start_pos: QPoint | None = None
        self._resize_start_geo: QRect | None = None
        self._is_maximized = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)

        self._setup_ui(title)
        self._apply_style()

    def _setup_ui(self, title: str):
        t = get_current_theme()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 6, 6)
        layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {t.text_primary};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.minimize_btn = MinimizeButton(self)
        self.minimize_btn.setToolTip("Minimize")
        self.minimize_btn.clicked.connect(self._on_minimize)
        layout.addWidget(self.minimize_btn)

        self.maximize_btn = MaximizeButton(self)
        self.maximize_btn.setToolTip("Maximize")
        self.maximize_btn.clicked.connect(self._on_maximize)
        layout.addWidget(self.maximize_btn)

        self.close_btn = CloseButton(self)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self._on_close)
        layout.addWidget(self.close_btn)

        self.setFixedHeight(48)

    def _apply_style(self):
        t = get_current_theme()
        self.setStyleSheet(f"""
            TitleBar {{
                background-color: {t.bg_primary};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
        """)
        # Update title label color
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {t.text_primary};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """)

    def refresh_theme(self):
        """Refresh title bar and button styles from current theme."""
        self._apply_style()
        # Refresh button styles
        self.minimize_btn._apply_base_style()
        self.maximize_btn._apply_base_style()
        self.close_btn._apply_base_style()
        self.update()

    def set_title(self, title: str):
        self.title_label.setText(title)

    def _on_minimize(self):
        self.window.showMinimized()

    def _on_maximize(self):
        if self._is_maximized:
            self.window.showNormal()
            self._is_maximized = False
        else:
            self.window.showMaximized()
            self._is_maximized = True
        self.maximize_btn.set_maximized(self._is_maximized)

    def _on_close(self):
        self.window.close()

    def _get_resize_edge(self, pos: QPoint) -> str:
        """Get resize edge if cursor is on top edge of title bar."""
        if pos.y() >= RESIZE_MARGIN:
            return ""

        if pos.x() < RESIZE_MARGIN * 2:
            return "topleft"
        elif pos.x() > self.width() - RESIZE_MARGIN * 2:
            return "topright"
        return "top"

    def _edge_to_qt_edges(self, edge: str):
        """Convert edge string to Qt.Edges flags for startSystemResize."""
        from PySide6.QtCore import Qt
        edges = Qt.Edge(0)
        if "top" in edge:
            edges |= Qt.Edge.TopEdge
        if "bottom" in edge:
            edges |= Qt.Edge.BottomEdge
        if "left" in edge:
            edges |= Qt.Edge.LeftEdge
        if "right" in edge:
            edges |= Qt.Edge.RightEdge
        return edges

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        pos = event.pos()
        edge = self._get_resize_edge(pos)

        if edge:
            # Try system resize first (works on Wayland)
            window_handle = self.window.windowHandle()
            if window_handle:
                qt_edges = self._edge_to_qt_edges(edge)
                if window_handle.startSystemResize(qt_edges):
                    event.accept()
                    return
            # Fallback to manual resize mode
            self._mode = self.MODE_RESIZE
            self._resize_edge = edge
            self._resize_start_pos = event.globalPosition().toPoint()
            self._resize_start_geo = self.window.geometry()
        else:
            # Restore from maximized if needed
            if self._is_maximized:
                self._on_maximize()  # Restore
            # Try system move first (works on Wayland)
            window_handle = self.window.windowHandle()
            if window_handle and window_handle.startSystemMove():
                event.accept()
                return
            # Fallback to manual drag mode
            self._mode = self.MODE_DRAG
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_window_pos = self.window.pos()

        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        # Handle resize mode (fallback for X11)
        if self._mode == self.MODE_RESIZE and self._resize_start_pos and self._resize_start_geo:
            self._do_resize(event.globalPosition().toPoint())
            event.accept()
            return

        # Handle drag mode (fallback for X11)
        if self._mode == self.MODE_DRAG and self._drag_start_pos and self._drag_start_window_pos:
            delta = event.globalPosition().toPoint() - self._drag_start_pos
            new_pos = self._drag_start_window_pos + delta
            self.window.move(new_pos)
            event.accept()
            return

        # Update cursor when not dragging/resizing
        edge = self._get_resize_edge(event.pos())
        if edge == "topleft":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge == "topright":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge == "top":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def _do_resize(self, global_pos: QPoint):
        """Perform the resize operation."""
        if not self._resize_start_pos or not self._resize_start_geo:
            return

        delta = global_pos - self._resize_start_pos
        geo = self._resize_start_geo
        min_w = self.window.minimumWidth() or 200
        min_h = self.window.minimumHeight() or 200

        x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()

        if "top" in self._resize_edge:
            # Dragging top edge: move y, adjust height inversely
            new_h = h - delta.y()
            if new_h >= min_h:
                y = geo.y() + delta.y()
                h = new_h

        if "left" in self._resize_edge:
            new_w = w - delta.x()
            if new_w >= min_w:
                x = geo.x() + delta.x()
                w = new_w

        if "right" in self._resize_edge:
            new_w = w + delta.x()
            if new_w >= min_w:
                w = new_w

        self.window.setGeometry(x, y, w, h)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mode = self.MODE_NONE
            self._drag_start_pos = None
            self._drag_start_window_pos = None
            self._resize_start_pos = None
            self._resize_start_geo = None
            self._resize_edge = ""
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._get_resize_edge(event.pos()):
                self._on_maximize()
