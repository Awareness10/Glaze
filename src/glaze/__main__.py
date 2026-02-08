"""Interactive launcher for glaze components.

Run with: python -m glaze
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QVBoxLayout, QFileDialog, QButtonGroup, QRadioButton,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from glaze.components import (
    LoginWindow, DataTableWindow, SettingsDialog, AwShellSettings
)

from glaze.widgets import FramelessMainWindow, ThemedComboBox
from glaze.color_backend import (
    generate_theme, get_backend_info,
    MATUGEN_SCHEMES, SCHEME_DISPLAY_NAMES,
)
from glaze.matugen import is_matugen_available
import glaze


class ComponentLauncher(FramelessMainWindow):
    """Interactive launcher to select which component to run."""

    def __init__(self):
        self.active_window = self
        super().__init__(width=500, height=860, title="Glaze Launcher")

    def get_extra_stylesheet(self) -> str:
        """Add custom styles for the theme settings group."""
        from glaze import get_current_theme
        t = get_current_theme()
        return f"""
            QGroupBox {{
                background-color: {t.bg_secondary};
                border: 1px solid {t.border};
                border-radius: 10px;
                margin-top: 16px;
                font-size: 13px;
            }}
            QGroupBox::title {{
                color: {t.text_primary};
                font-weight: 600;
                font-size: 13px;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                left: 12px;
            }}
            QRadioButton {{
                color: {t.text_primary};
                spacing: 8px;
                font-size: 13px;
                padding: 4px 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {t.border};
                border-radius: 10px;
                background-color: transparent;
            }}
            QRadioButton::indicator:checked {{
                background-color: {t.accent};
                border-color: {t.accent};
            }}
            QRadioButton::indicator:hover {{
                border-color: {t.accent};
            }}
        """

    def setup_content(self):
        self.content_layout.setContentsMargins(40, 30, 40, 40)
        self.content_layout.setSpacing(16)

        # Title
        title = QLabel("Glaze Launcher")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title)

        subtitle = QLabel("Choose a component to launch")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(subtitle)

        self.content_layout.addSpacing(8)

        # Theme controls group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(12)
        theme_layout.setContentsMargins(16, 28, 16, 16)

        # Wallpaper picker
        wallpaper_layout = QHBoxLayout()
        wallpaper_layout.setSpacing(10)
        wallpaper_label = QLabel("Wallpaper:")
        wallpaper_label.setFixedWidth(75)
        wallpaper_layout.addWidget(wallpaper_label)
        self.auto_apply_theme = False
        # Aw-Shell support
        if (Path.home() / ".current.wall").is_file():
            self.wallpaper_path = QLineEdit(text=str(Path.home().resolve() / '.current.wall'))
            self.auto_apply_theme = True
        else:
            self.wallpaper_path = QLineEdit(placeholderText="Select wallpaper image...")

        self.wallpaper_path.setReadOnly(True)
        self.wallpaper_path.setMinimumHeight(38)
        wallpaper_layout.addWidget(self.wallpaper_path)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(80)
        browse_btn.setMinimumHeight(38)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse_wallpaper)
        wallpaper_layout.addWidget(browse_btn)

        theme_layout.addLayout(wallpaper_layout)

        # Scheme selector
        scheme_layout = QHBoxLayout()
        scheme_layout.setSpacing(10)
        scheme_label = QLabel("Scheme:")
        scheme_label.setFixedWidth(75)
        scheme_layout.addWidget(scheme_label)

        self.scheme_combo = ThemedComboBox()
        self.scheme_combo.setMinimumHeight(38)
        for scheme in MATUGEN_SCHEMES:
            display_name = SCHEME_DISPLAY_NAMES.get(scheme, scheme)
            self.scheme_combo.addItem(display_name, scheme)
        scheme_layout.addWidget(self.scheme_combo)

        theme_layout.addLayout(scheme_layout)

        # Mode selector (System/Dark/Light)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        mode_label = QLabel("Mode:")
        mode_label.setFixedWidth(75)
        mode_layout.addWidget(mode_label)

        self.mode_group = QButtonGroup(self)

        self.system_mode_radio = QRadioButton("System")
        self.system_mode_radio.setMinimumHeight(32)
        self.mode_group.addButton(self.system_mode_radio, 0)
        mode_layout.addWidget(self.system_mode_radio)

        self.dark_mode_radio = QRadioButton("Dark")
        self.dark_mode_radio.setChecked(True)
        self.dark_mode_radio.setMinimumHeight(32)
        self.mode_group.addButton(self.dark_mode_radio, 1)
        mode_layout.addWidget(self.dark_mode_radio)

        self.light_mode_radio = QRadioButton("Light")
        self.light_mode_radio.setMinimumHeight(32)
        self.mode_group.addButton(self.light_mode_radio, 2)
        mode_layout.addWidget(self.light_mode_radio)

        mode_layout.addStretch()
        theme_layout.addLayout(mode_layout)

        # Backend selector
        backend_layout = QHBoxLayout()
        backend_layout.setSpacing(10)
        backend_label = QLabel("Backend:")
        backend_label.setFixedWidth(75)
        backend_layout.addWidget(backend_label)

        self.backend_group = QButtonGroup(self)

        self.auto_radio = QRadioButton("Auto")
        self.auto_radio.setChecked(True)
        self.auto_radio.setMinimumHeight(32)
        self.backend_group.addButton(self.auto_radio, 0)
        backend_layout.addWidget(self.auto_radio)

        self.matugen_radio = QRadioButton("Matugen")
        self.matugen_radio.setMinimumHeight(32)
        self.backend_group.addButton(self.matugen_radio, 1)
        backend_layout.addWidget(self.matugen_radio)

        self.pillow_radio = QRadioButton("Pillow")
        self.pillow_radio.setMinimumHeight(32)
        self.backend_group.addButton(self.pillow_radio, 2)
        backend_layout.addWidget(self.pillow_radio)

        backend_layout.addStretch()
        theme_layout.addLayout(backend_layout)

        # Backend status
        backend_info = get_backend_info()
        matugen_status = "installed" if backend_info["matugen"] else "not found"
        status_text = f"Matugen: {matugen_status}"
        self.status_label = QLabel(status_text)
        self.status_label.setObjectName("subtitle")
        theme_layout.addWidget(self.status_label)

        # Update scheme combo state based on backend
        self.backend_group.buttonClicked.connect(self._on_backend_changed)
        self._update_scheme_state()

        # Apply theme button
        apply_btn = QPushButton("Apply Theme")
        apply_btn.setMinimumHeight(42)
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.clicked.connect(self.apply_theme)
        theme_layout.addWidget(apply_btn)

        self.content_layout.addWidget(theme_group)

        self.content_layout.addSpacing(8)

        # Component buttons
        login_btn = QPushButton("Login Form")
        login_btn.setMinimumHeight(50)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.launch_login)
        self.content_layout.addWidget(login_btn)

        data_table_btn = QPushButton("Data Table Manager")
        data_table_btn.setMinimumHeight(50)
        data_table_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        data_table_btn.clicked.connect(self.launch_data_table)
        self.content_layout.addWidget(data_table_btn)

        settings_btn = QPushButton("Settings Dialog")
        settings_btn.setMinimumHeight(50)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.launch_settings)
        self.content_layout.addWidget(settings_btn)

        aw_settings_btn = QPushButton("AwSettings Dialog")
        aw_settings_btn.setMinimumHeight(50)
        aw_settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        aw_settings_btn.clicked.connect(self.launch_aw_settings)
        self.content_layout.addWidget(aw_settings_btn)

        self.content_layout.addStretch()

        # Info label
        info = QLabel("Each component demonstrates PySide6 theming")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setObjectName("subtitle")
        info.setStyleSheet("font-size: 11px;")
        self.content_layout.addWidget(info)

        if self.auto_apply_theme:
            self.apply_theme()

    def browse_wallpaper(self):
        """Open file dialog to select wallpaper image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wallpaper Image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*)"
        )
        if file_path:
            self.wallpaper_path.setText(file_path)

    def _on_backend_changed(self):
        """Handle backend selection change."""
        self._update_scheme_state()

    def _update_scheme_state(self):
        """Update scheme combo enabled state based on backend."""
        # Disable scheme selection if pillow is explicitly selected
        if self.pillow_radio.isChecked():
            self.scheme_combo.setEnabled(False)
            self.scheme_combo.setToolTip("Scheme selection requires matugen backend")
        elif self.matugen_radio.isChecked() and not is_matugen_available():
            self.scheme_combo.setEnabled(False)
            self.scheme_combo.setToolTip("Matugen is not installed")
        else:
            self.scheme_combo.setEnabled(True)
            self.scheme_combo.setToolTip("")

    def _get_selected_backend(self) -> str:
        """Get the selected backend name."""
        checked_id = self.backend_group.checkedId()
        return ["auto", "matugen", "pillow"][checked_id]

    def _get_selected_scheme(self) -> str:
        """Get the selected scheme name."""
        return self.scheme_combo.currentData()

    def _get_dark_mode(self) -> bool:
        """Get dark mode based on selected mode (System/Dark/Light)."""
        checked_id = self.mode_group.checkedId()
        if checked_id == 0:  # System
            return self._detect_system_dark_mode()
        elif checked_id == 1:  # Dark
            return True
        else:  # Light
            return False

    def _detect_system_dark_mode(self) -> bool:
        """Detect system dark mode preference.

        Checks freedesktop color-scheme setting via dbus or gsettings.
        Falls back to dark mode if detection fails.
        """
        import subprocess
        try:
            # Try freedesktop portal (works on most modern Linux desktops)
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "dark" in result.stdout.lower()
        except Exception:
            pass

        try:
            # Try GTK theme name as fallback
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "dark" in result.stdout.lower()
        except Exception:
            pass

        # Default to dark mode if detection fails
        return True

    def apply_theme(self):
        """Apply theme from wallpaper with selected scheme and backend."""
        wallpaper = self.wallpaper_path.text()

        if not wallpaper:
            self._show_status("Please select a wallpaper image", error=True)
            return

        if not Path(wallpaper).exists():
            self._show_status(f"File not found: {wallpaper}", error=True)
            return

        backend = self._get_selected_backend()
        scheme = self._get_selected_scheme()
        dark_mode = self._get_dark_mode()

        try:
            theme, used_backend = generate_theme(
                image_path=wallpaper,
                scheme=scheme,
                dark_mode=dark_mode,
                backend=backend,
            )

            # Update global theme
            glaze.theme = theme

            # Update theme module directly
            import sys
            theme_module = sys.modules['glaze.theme']
            theme_module.theme = theme

            # Refresh theme on this window (updates stylesheet, title bar, etc.)
            self.refresh_theme()

            # Refresh any active component windows
            #if self.active_window and hasattr(self.active_window, 'refresh_theme'):
            #    self.active_window.refresh_theme()

            # Show success
            mode_str = "dark" if dark_mode else "light"
            scheme_display = SCHEME_DISPLAY_NAMES.get(scheme, scheme)
            self._show_status(f"Theme applied: {used_backend} ({scheme_display}, {mode_str})")

        except RuntimeError as e:
            self._show_status(str(e), error=True)
        except Exception as e:
            if e in [AttributeError]:
                ...
            else:
                self._show_status(f"Error: {e}", error=True)

    def _show_status(self, message: str, error: bool = False):
        """Update status label with message."""
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: #cf6679;")
        else:
            self.status_label.setStyleSheet(f"color: {glaze.theme.accent};")

        # Reset after 3 seconds
        from PySide6.QtCore import QTimer
        backend_info = get_backend_info()
        matugen_status = "installed" if backend_info["matugen"] else "not found"

        def reset():
            self.status_label.setText(f"Matugen: {matugen_status}")
            self.status_label.setStyleSheet("")

        QTimer.singleShot(3000, reset)

    def launch_login(self):
        #if self.active_window:
        #    self.active_window.close()
        self.active_window = LoginWindow()
        self.active_window.show()

    def launch_data_table(self):
        #if self.active_window:
        #    self.active_window.close()
        self.active_window = DataTableWindow()
        self.active_window.show()

    def launch_settings(self):
        pass
        dialog = SettingsDialog(self)
        dialog.exec()

    def launch_aw_settings(self):
        #if self.active_window:
        #    self.active_window.close()
        self.active_window = AwShellSettings()
        self.active_window.show()
        

def main():
    app = QApplication(sys.argv)
    launcher = ComponentLauncher()
    launcher.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
