"""Themed ComboBox widget with proper Linux Qt6 dropdown styling."""

from PySide6.QtWidgets import QComboBox, QListView, QFrame
from PySide6.QtCore import Qt


def _get_popup_frame_style(t) -> str:
    """Generate popup frame style for combobox dropdowns."""
    return f"""
        QFrame {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: 4px;
            margin: 0;
            padding: 0;
        }}
    """


class ThemedComboBox(QComboBox):
    """ComboBox with fully themed dropdown for Linux Qt6.

    This widget relies on the base stylesheet from theme.py for consistent
    styling including the dropdown arrow. It adds custom popup/view handling
    to fix Linux Qt6 dropdown rendering issues.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_view()

    def _setup_view(self):
        from glaze.theme import theme, _get_listview_styles

        view = QListView()
        view.setStyleSheet(_get_listview_styles(theme, variant="popup"))
        if view.viewport():
            view.viewport().setStyleSheet(f"background-color: {theme.bg_secondary}; margin: 0; padding: 0;")  # type: ignore
        self.setView(view)

    def showPopup(self):
        from glaze.theme import theme

        super().showPopup()
        popup = self.findChild(QFrame)
        if popup:
            popup.setWindowFlags(
                Qt.WindowType.Popup |
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.NoDropShadowWindowHint
            )
            popup.setStyleSheet(_get_popup_frame_style(theme))
            popup.setContentsMargins(0, 0, 0, 0)
            popup.show()


def style_combobox(combo: QComboBox) -> None:
    """Apply custom view to combobox for proper dark theme styling."""
    from glaze.theme import theme, _get_listview_styles

    view = QListView()
    view.setStyleSheet(_get_listview_styles(theme, variant="standalone"))

    if view.viewport():
        view.viewport().setStyleSheet(f"background-color: {theme.bg_secondary};")  # type: ignore

    combo.setView(view)

    # Force popup to be frameless and remove margins
    popup = combo.findChild(QFrame)
    if popup:
        popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        popup.setStyleSheet(_get_popup_frame_style(theme))
