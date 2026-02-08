"""Base class for frameless main windows with custom decorations.

This module provides a FramelessMainWindow base class that consolidates
the common resize/paint logic needed for frameless windows with rounded
corners and custom title bars.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QPoint, QRect, QTimer
from PySide6.QtGui import (
    QPainter, QBrush, QColor, QPainterPath, QMouseEvent, QRegion, QShowEvent
)

from ..theme import get_current_theme, get_base_stylesheet
from ..wayland import make_window_frameless, hyprctl_float_active
from .title_bar import TitleBar

# Constants
RESIZE_MARGIN = 8
CORNER_RADIUS = 10


class FramelessMainWindow(QMainWindow):
    """Base class for frameless main windows with rounded corners and resize support.

    This class provides:
    - Frameless window setup via make_window_frameless()
    - Rounded corner painting with theme colors
    - Window mask for compositor transparency
    - Edge-based resize with Wayland system resize support (fallback to manual)
    - Common UI structure: TitleBar + content area with QVBoxLayout

    Subclasses should:
    - Override setup_content() to add their UI to self.content_layout
    - Override get_extra_stylesheet() for additional styles
    - Pass width, height, and title to __init__()

    Example:
        class MyWindow(FramelessMainWindow):
            def __init__(self):
                super().__init__(400, 300, "My App")

            def setup_content(self):
                label = QLabel("Hello World")
                self.content_layout.addWidget(label)
    """

    def __init__(self, width: int, height: int, title: str):
        """Initialize the frameless main window.

        Args:
            width: Initial window width
            height: Initial window height
            title: Window title displayed in the title bar
        """
        super().__init__()
        self._floating = True  # Track floating preference
        make_window_frameless(self, width, height, floating=self._floating)
        self._init_resize_state()
        self._setup_base_ui(title)
        self.setup_content()
        self._apply_stylesheet()

    def showEvent(self, event: QShowEvent):
        """Handle show event - float window on Hyprland after display."""
        super().showEvent(event)
        # Use a short delay to ensure window is mapped before floating
        if self._floating:
            QTimer.singleShot(50, hyprctl_float_active)

    def _init_resize_state(self):
        """Initialize resize tracking variables."""
        self._resize_edge: str | None = None
        self._resize_start_pos: QPoint | None = None
        self._resize_start_geometry: QRect | None = None
        self.setMouseTracking(True)

    def _setup_base_ui(self, title: str):
        """Create container, TitleBar, and content frame.

        Args:
            title: Window title for the title bar
        """
        # Main container widget
        self._container = QWidget()
        self._container.setObjectName("windowContainer")
        self._container.setMouseTracking(True)

        main_layout = QVBoxLayout(self._container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self, title=title)
        main_layout.addWidget(self.title_bar)

        # Content frame
        self._content_frame = QFrame()
        self._content_frame.setObjectName("contentArea")
        self._content_frame.setMouseTracking(True)

        self.content_layout = QVBoxLayout(self._content_frame)
        # Default margins - subclasses can override in setup_content()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        main_layout.addWidget(self._content_frame)

        self.setCentralWidget(self._container)

    def setup_content(self):
        """Set up the window content. Override in subclasses.

        Add widgets to self.content_layout in your override.
        You can also adjust content_layout margins/spacing here.

        Example:
            def setup_content(self):
                self.content_layout.setContentsMargins(20, 20, 20, 20)
                self.content_layout.setSpacing(10)

                label = QLabel("Hello")
                self.content_layout.addWidget(label)
        """
        pass

    def get_extra_stylesheet(self) -> str:
        """Return additional stylesheet rules. Override in subclasses.

        Returns:
            CSS stylesheet string to append to the base stylesheet
        """
        return ""

    def _apply_stylesheet(self):
        """Combine and apply base + extra stylesheets."""
        base_styles = get_base_stylesheet()
        frameless_styles = """
            QMainWindow {
                background: transparent;
            }
            #windowContainer {
                background-color: transparent;
                border: none;
            }
            #contentArea {
                background-color: transparent;
            }
        """
        extra_styles = self.get_extra_stylesheet()
        self.setStyleSheet(base_styles + frameless_styles + extra_styles)

    def refresh_theme(self):
        """Refresh all theme-dependent elements.

        Call this after changing the global theme to update:
        - Window stylesheet
        - Title bar colors
        - Window background (via repaint)
        """
        self._apply_stylesheet()
        self.title_bar.refresh_theme()
        self.update()  # Trigger repaint for rounded corners

    def paintEvent(self, event):
        """Draw rounded corners with theme colors (no border, like Kitty)."""
        t = get_current_theme()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Full rect with rounded corners, no border
        path = QPainterPath()
        path.addRoundedRect(
            0, 0,
            self.width(), self.height(),
            CORNER_RADIUS, CORNER_RADIUS
        )

        # Fill background only - no border for clean Kitty-like look
        painter.fillPath(path, QBrush(QColor(t.bg_primary)))

    def resizeEvent(self, event):
        """Update window mask to inform compositor of rounded corners."""
        path = QPainterPath()
        path.addRoundedRect(
            0, 0,
            self.width(), self.height(),
            CORNER_RADIUS, CORNER_RADIUS
        )
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        super().resizeEvent(event)

    def _get_resize_edge(self, pos: QPoint) -> str | None:
        """Determine which edge the cursor is on.

        Args:
            pos: Mouse position relative to window

        Returns:
            Edge string (e.g., "top", "bottomleft") or None if not on edge
        """
        rect = self.rect()
        x, y = pos.x(), pos.y()
        w, h = rect.width(), rect.height()
        m = RESIZE_MARGIN

        edges = []

        if y < m:
            edges.append("top")
        elif y > h - m:
            edges.append("bottom")

        if x < m:
            edges.append("left")
        elif x > w - m:
            edges.append("right")

        return "".join(edges) if edges else None

    def _get_cursor_for_edge(self, edge: str | None) -> Qt.CursorShape:
        """Get the appropriate cursor shape for an edge.

        Args:
            edge: Edge string or None

        Returns:
            Qt cursor shape for the edge
        """
        cursors = {
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "topleft": Qt.CursorShape.SizeFDiagCursor,
            "bottomright": Qt.CursorShape.SizeFDiagCursor,
            "topright": Qt.CursorShape.SizeBDiagCursor,
            "bottomleft": Qt.CursorShape.SizeBDiagCursor,
        }
        return cursors.get(edge, Qt.CursorShape.ArrowCursor)

    def _edge_to_qt_edges(self, edge: str) -> Qt.Edge:
        """Convert edge string to Qt.Edge flags for startSystemResize.

        Args:
            edge: Edge string (e.g., "topleft", "bottom")

        Returns:
            Qt.Edge flags
        """
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
        """Handle mouse press for resize initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_resize_edge(event.pos())
            if edge:
                # Try system resize first (works on Wayland)
                window_handle = self.windowHandle()
                if window_handle:
                    qt_edges = self._edge_to_qt_edges(edge)
                    if window_handle.startSystemResize(qt_edges):
                        event.accept()
                        return

                # Fallback to manual resize
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for resize and cursor updates."""
        if (
            self._resize_edge
            and self._resize_start_pos
            and self._resize_start_geometry
        ):
            # Perform manual resize
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            geo = QRect(self._resize_start_geometry)
            min_w = self.minimumWidth() or 200
            min_h = self.minimumHeight() or 200

            if "left" in self._resize_edge:
                new_width = geo.right() - (geo.left() + delta.x()) + 1
                if new_width >= min_w:
                    geo.setLeft(geo.left() + delta.x())

            if "right" in self._resize_edge:
                if geo.width() + delta.x() >= min_w:
                    geo.setWidth(geo.width() + delta.x())

            if "top" in self._resize_edge:
                new_height = geo.bottom() - (geo.top() + delta.y()) + 1
                if new_height >= min_h:
                    geo.setTop(geo.top() + delta.y())

            if "bottom" in self._resize_edge:
                if geo.height() + delta.y() >= min_h:
                    geo.setHeight(geo.height() + delta.y())

            self.setGeometry(geo)
            event.accept()
            return
        else:
            # Update cursor based on edge
            edge = self._get_resize_edge(event.pos())
            if edge:
                self.setCursor(self._get_cursor_for_edge(edge))
            else:
                self.unsetCursor()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to end resize operation."""
        if event.button() == Qt.MouseButton.LeftButton and self._resize_edge:
            self._resize_edge = None
            self._resize_start_pos = None
            self._resize_start_geometry = None
            event.accept()
            return

        super().mouseReleaseEvent(event)
