"""Settings/Preferences dialog component.

A professional settings dialog with:
- Responsive tabbed interface that handles resize gracefully
- Scrollable tab content for overflow handling
- Clean section layout with proper spacing
- Theme-consistent styling
- Working theme selection with wallpaper/scheme support
"""
from typing import cast
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QCheckBox,
    QRadioButton,
    QSlider,
    QSpinBox,
    QPushButton,
    QButtonGroup,
    QGroupBox,
    QMessageBox,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QLineEdit,
    QFileDialog,
)

from glaze.theme import get_dialog_stylesheet, get_table_container_style, get_current_theme
from glaze.widgets import ThemedComboBox, FramelessMainWindow, DonateButton
from glaze.color_backend import (
    generate_theme, get_backend_info,
    MATUGEN_SCHEMES, SCHEME_DISPLAY_NAMES, Backend
)
from glaze.matugen import is_matugen_available
import glaze


class SettingsSection(QGroupBox):
    """A styled section container for settings groups."""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class SettingsDialog(FramelessMainWindow):
    """Modern settings dialog with tabbed interface and custom titlebar."""

    def __init__(self, parent=None):
        self.settings = QSettings("Glaze", "SettingsDemo")
        super().__init__(width=600, height=940, title="Settings")
        self.setMinimumSize(500, 400)
        self.load_settings()
        self._restore_window_geometry()

    def _restore_window_geometry(self):
        """Restore window position and size if enabled."""
        if self.settings.value("general/remember_window", True, bool):
            geometry = self.settings.value("window/geometry")
            if geometry:
                self.restoreGeometry(geometry)

    def closeEvent(self, event):
        """Save window geometry on close if enabled."""
        if self.remember_window_cb.isChecked():
            self.settings.setValue("window/geometry", self.saveGeometry())
            self.settings.sync()
        super().closeEvent(event)

    def setup_content(self):
        """Set up the settings dialog content."""
        self.content_layout.setContentsMargins(16, 12, 16, 16)
        self.content_layout.setSpacing(12)

        # Tab widget container with shadow
        tab_container = QFrame()
        tab_container.setObjectName("tableContainer")
        tab_container.setStyleSheet(get_table_container_style())
        tab_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 80))
        tab_container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(tab_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.tabs.addTab(self._create_scrollable_tab(self.create_general_tab()), "General")
        self.tabs.addTab(self._create_scrollable_tab(self.create_appearance_tab()), "Appearance")
        self.tabs.addTab(self._create_scrollable_tab(self.create_advanced_tab()), "Advanced")

        container_layout.addWidget(self.tabs)
        self.content_layout.addWidget(tab_container, 1)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        donate_btn = DonateButton(url="https://ko-fi.com/awareness10")
        button_layout.addWidget(donate_btn)

        button_layout.addStretch()

        self.restore_btn = QPushButton("Restore Defaults")
        self.restore_btn.setObjectName("secondary")
        self.restore_btn.clicked.connect(self.restore_defaults)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.close)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("secondary")
        self.apply_btn.clicked.connect(self.apply_settings)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_and_apply)

        for btn in [self.restore_btn, self.cancel_btn, self.apply_btn, self.ok_btn]:
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(90)

        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.ok_btn)

        self.content_layout.addLayout(button_layout)

    def get_extra_stylesheet(self) -> str:
        """Return dialog-specific styles."""
        t = get_current_theme()
        return get_dialog_stylesheet() + f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            SettingsSection {{
                font-weight: 600;
                padding-top: 8px;
            }}
            SettingsSection::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                color: {t.text_primary};
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

    def _create_scrollable_tab(self, content: QWidget) -> QScrollArea:
        """Wrap tab content in a scroll area for overflow handling."""
        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    def exec(self):
        """Show window modally (compatibility with QDialog interface)."""
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()

    # -------------------------------------------------------------------------
    # Tab Creation
    # -------------------------------------------------------------------------

    def create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Startup section
        startup_section = SettingsSection("Startup")
        startup_layout = QVBoxLayout(startup_section)
        startup_layout.setSpacing(8)

        self.auto_start_cb = QCheckBox("Launch on system startup")
        self.remember_window_cb = QCheckBox("Remember window position and size")
        self.restore_session_cb = QCheckBox("Restore previous session")

        startup_layout.addWidget(self.auto_start_cb)
        startup_layout.addWidget(self.remember_window_cb)
        startup_layout.addWidget(self.restore_session_cb)
        layout.addWidget(startup_section)

        # Language & Region section
        language_section = SettingsSection("Language && Region")
        language_layout = QFormLayout(language_section)
        language_layout.setSpacing(12)
        language_layout.setHorizontalSpacing(16)
        language_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.language_combo = ThemedComboBox()
        self.language_combo.addItems(["English", "Espanol", "Francais", "Deutsch", "Japanese"])
        self.language_combo.setMinimumWidth(180)

        self.date_format_combo = ThemedComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        self.date_format_combo.setMinimumWidth(180)

        language_layout.addRow("Language:", self.language_combo)
        language_layout.addRow("Date Format:", self.date_format_combo)
        layout.addWidget(language_section)

        # Auto-save section
        autosave_section = SettingsSection("Auto-save")
        autosave_layout = QVBoxLayout(autosave_section)
        autosave_layout.setSpacing(10)

        self.autosave_cb = QCheckBox("Enable auto-save")
        self.autosave_cb.setChecked(True)
        autosave_layout.addWidget(self.autosave_cb)

        interval_row = QHBoxLayout()
        interval_row.setSpacing(10)
        interval_row.addWidget(QLabel("Save interval:"))
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setValue(5)
        self.autosave_spin.setSuffix(" min")
        self.autosave_spin.setMinimumWidth(80)
        interval_row.addWidget(self.autosave_spin)
        interval_row.addStretch()
        autosave_layout.addLayout(interval_row)
        layout.addWidget(autosave_section)

        layout.addStretch()
        return widget

    def create_appearance_tab(self) -> QWidget:
        """Create the Appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Theme section
        theme_section = SettingsSection("Theme")
        theme_layout = QVBoxLayout(theme_section)
        theme_layout.setSpacing(12)

        # Mode selector (System/Dark/Light)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        mode_label = QLabel("Mode:")
        mode_label.setFixedWidth(80)
        mode_layout.addWidget(mode_label)

        self.theme_group = QButtonGroup(self)
        self.system_theme_rb = QRadioButton("System")
        self.system_theme_rb.setMinimumHeight(32)
        self.dark_theme_rb = QRadioButton("Dark")
        self.dark_theme_rb.setChecked(True)
        self.dark_theme_rb.setMinimumHeight(32)
        self.light_theme_rb = QRadioButton("Light")
        self.light_theme_rb.setMinimumHeight(32)

        self.theme_group.addButton(self.system_theme_rb, 0)
        self.theme_group.addButton(self.dark_theme_rb, 1)
        self.theme_group.addButton(self.light_theme_rb, 2)

        mode_layout.addWidget(self.system_theme_rb)
        mode_layout.addWidget(self.dark_theme_rb)
        mode_layout.addWidget(self.light_theme_rb)
        mode_layout.addStretch()
        theme_layout.addLayout(mode_layout)

        # Wallpaper picker
        wallpaper_layout = QHBoxLayout()
        wallpaper_layout.setSpacing(10)
        wallpaper_label = QLabel("Wallpaper:")
        wallpaper_label.setFixedWidth(80)
        wallpaper_layout.addWidget(wallpaper_label)

        self.wallpaper_path = QLineEdit()
        self.wallpaper_path.setPlaceholderText("Select wallpaper for Material You theme...")
        self.wallpaper_path.setReadOnly(True)
        self.wallpaper_path.setMinimumHeight(36)
        wallpaper_layout.addWidget(self.wallpaper_path)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedWidth(80)
        browse_btn.setMinimumHeight(36)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_wallpaper)
        wallpaper_layout.addWidget(browse_btn)
        theme_layout.addLayout(wallpaper_layout)

        # Scheme selector
        scheme_layout = QHBoxLayout()
        scheme_layout.setSpacing(10)
        scheme_label = QLabel("Scheme:")
        scheme_label.setFixedWidth(80)
        scheme_layout.addWidget(scheme_label)

        self.scheme_combo = ThemedComboBox()
        self.scheme_combo.setMinimumHeight(36)
        for scheme in MATUGEN_SCHEMES:
            display_name = SCHEME_DISPLAY_NAMES.get(scheme, scheme)
            self.scheme_combo.addItem(display_name, scheme)
        scheme_layout.addWidget(self.scheme_combo)
        theme_layout.addLayout(scheme_layout)

        # Backend selector
        backend_layout = QHBoxLayout()
        backend_layout.setSpacing(10)
        backend_label = QLabel("Backend:")
        backend_label.setFixedWidth(80)
        backend_layout.addWidget(backend_label)

        self.backend_group = QButtonGroup(self)
        self.auto_backend_rb = QRadioButton("Auto")
        self.auto_backend_rb.setChecked(True)
        self.auto_backend_rb.setMinimumHeight(32)
        self.matugen_backend_rb = QRadioButton("Matugen")
        self.matugen_backend_rb.setMinimumHeight(32)
        self.pillow_backend_rb = QRadioButton("Pillow")
        self.pillow_backend_rb.setMinimumHeight(32)

        self.backend_group.addButton(self.auto_backend_rb, 0)
        self.backend_group.addButton(self.matugen_backend_rb, 1)
        self.backend_group.addButton(self.pillow_backend_rb, 2)

        backend_layout.addWidget(self.auto_backend_rb)
        backend_layout.addWidget(self.matugen_backend_rb)
        backend_layout.addWidget(self.pillow_backend_rb)
        backend_layout.addStretch()
        theme_layout.addLayout(backend_layout)

        # Backend status and apply button
        status_layout = QHBoxLayout()
        backend_info = get_backend_info()
        matugen_status = "installed" if backend_info["matugen"] else "not found"
        self.theme_status_label = QLabel(f"Matugen: {matugen_status}")
        self.theme_status_label.setObjectName("subtitle")
        status_layout.addWidget(self.theme_status_label)
        status_layout.addStretch()

        apply_theme_btn = QPushButton("Apply Theme")
        apply_theme_btn.setMinimumHeight(36)
        apply_theme_btn.setMinimumWidth(120)
        apply_theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_theme_btn.clicked.connect(self._apply_theme)
        status_layout.addWidget(apply_theme_btn)
        theme_layout.addLayout(status_layout)

        # Update scheme combo state based on backend
        self.backend_group.buttonClicked.connect(self._on_backend_changed)
        self._update_scheme_state()

        layout.addWidget(theme_section)

        # Interface Scale section
        scale_section = SettingsSection("Interface Scale")
        scale_layout = QVBoxLayout(scale_section)
        scale_layout.setSpacing(10)

        scale_row = QHBoxLayout()
        scale_row.setSpacing(12)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(80, 150)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setMinimumWidth(200)
        scale_row.addWidget(self.scale_slider, 1)

        self.scale_label = QLabel("100%")
        self.scale_label.setMinimumWidth(45)
        self.scale_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        scale_row.addWidget(self.scale_label)

        self.scale_slider.valueChanged.connect(lambda v: self.scale_label.setText(f"{v}%"))

        scale_layout.addLayout(scale_row)
        layout.addWidget(scale_section)

        # Font section
        font_section = SettingsSection("Font")
        font_layout = QFormLayout(font_section)
        font_layout.setSpacing(12)
        font_layout.setHorizontalSpacing(16)
        font_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.font_combo = ThemedComboBox()
        self.font_combo.addItems(["System Default", "Segoe UI", "Roboto", "San Francisco", "Noto Sans"])
        self.font_combo.setMinimumWidth(180)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(11)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setMinimumWidth(80)

        font_layout.addRow("Font Family:", self.font_combo)
        font_layout.addRow("Font Size:", self.font_size_spin)
        layout.addWidget(font_section)

        # Animations section
        animation_section = SettingsSection("Animations")
        animation_layout = QVBoxLayout(animation_section)
        animation_layout.setSpacing(8)

        self.animations_cb = QCheckBox("Enable animations")
        self.animations_cb.setChecked(True)
        self.smooth_scroll_cb = QCheckBox("Smooth scrolling")
        self.smooth_scroll_cb.setChecked(True)

        animation_layout.addWidget(self.animations_cb)
        animation_layout.addWidget(self.smooth_scroll_cb)
        layout.addWidget(animation_section)

        layout.addStretch()
        return widget

    def create_advanced_tab(self) -> QWidget:
        """Create the Advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Performance section
        performance_section = SettingsSection("Performance")
        performance_layout = QVBoxLayout(performance_section)
        performance_layout.setSpacing(10)

        self.hardware_accel_cb = QCheckBox("Enable hardware acceleration")
        self.hardware_accel_cb.setChecked(True)
        self.gpu_rendering_cb = QCheckBox("Use GPU rendering")

        performance_layout.addWidget(self.hardware_accel_cb)
        performance_layout.addWidget(self.gpu_rendering_cb)

        threads_row = QHBoxLayout()
        threads_row.setSpacing(10)
        threads_row.addWidget(QLabel("Worker threads:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setValue(4)
        self.threads_spin.setMinimumWidth(70)
        threads_row.addWidget(self.threads_spin)
        threads_row.addStretch()
        performance_layout.addLayout(threads_row)
        layout.addWidget(performance_section)

        # Cache section
        cache_section = SettingsSection("Cache")
        cache_layout = QVBoxLayout(cache_section)
        cache_layout.setSpacing(10)

        cache_row = QHBoxLayout()
        cache_row.setSpacing(10)
        cache_row.addWidget(QLabel("Cache size:"))
        self.cache_spin = QSpinBox()
        self.cache_spin.setRange(50, 5000)
        self.cache_spin.setValue(500)
        self.cache_spin.setSingleStep(50)
        self.cache_spin.setSuffix(" MB")
        self.cache_spin.setMinimumWidth(100)
        cache_row.addWidget(self.cache_spin)
        cache_row.addStretch()
        cache_layout.addLayout(cache_row)

        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.setObjectName("secondary")
        self.clear_cache_btn.setMaximumWidth(120)
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(self.clear_cache_btn)
        layout.addWidget(cache_section)

        # Developer Options section
        dev_section = SettingsSection("Developer Options")
        dev_layout = QVBoxLayout(dev_section)
        dev_layout.setSpacing(8)

        self.debug_mode_cb = QCheckBox("Enable debug mode")
        self.verbose_logging_cb = QCheckBox("Verbose logging")
        self.show_fps_cb = QCheckBox("Show FPS counter")

        dev_layout.addWidget(self.debug_mode_cb)
        dev_layout.addWidget(self.verbose_logging_cb)
        dev_layout.addWidget(self.show_fps_cb)
        layout.addWidget(dev_section)

        layout.addStretch()
        return widget

    # -------------------------------------------------------------------------
    # Theme Methods
    # -------------------------------------------------------------------------

    def _browse_wallpaper(self):
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
        if self.pillow_backend_rb.isChecked():
            self.scheme_combo.setEnabled(False)
            self.scheme_combo.setToolTip("Scheme selection requires matugen backend")
        elif self.matugen_backend_rb.isChecked() and not is_matugen_available():
            self.scheme_combo.setEnabled(False)
            self.scheme_combo.setToolTip("Matugen is not installed")
        else:
            self.scheme_combo.setEnabled(True)
            self.scheme_combo.setToolTip("")

    def _get_selected_backend(self) -> Backend:
        """Get the selected backend name."""
        checked_id = self.backend_group.checkedId()
        backends: tuple[Backend, ...] = ("auto", "matugen", "pillow")
        return backends[checked_id]

    def _get_selected_scheme(self) -> str:
        """Get the selected scheme name."""
        return self.scheme_combo.currentData()

    def _get_dark_mode(self) -> bool:
        """Get dark mode based on selected mode (System/Dark/Light)."""
        checked_id = self.theme_group.checkedId()
        if checked_id == 0:  # System
            return self._detect_system_dark_mode()
        elif checked_id == 1:  # Dark
            return True
        else:  # Light
            return False

    def _detect_system_dark_mode(self) -> bool:
        """Detect system dark mode preference."""
        import subprocess
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "dark" in result.stdout.lower()
        except Exception:
            pass
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "dark" in result.stdout.lower()
        except Exception:
            pass
        return True  # Default to dark

    def _apply_theme(self):
        """Apply theme from wallpaper with selected scheme and backend."""
        wallpaper = self.wallpaper_path.text()

        if not wallpaper:
            self._show_theme_status("Please select a wallpaper image", error=True)
            return

        if not Path(wallpaper).exists():
            self._show_theme_status(f"File not found: {wallpaper}", error=True)
            return

        backend: Backend = self._get_selected_backend()
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
            theme_module.theme = theme # pyright: ignore[reportAttributeAccessIssue]

            # Refresh theme on this window
            self.refresh_theme()

            # Show success
            mode_str = "dark" if dark_mode else "light"
            scheme_display = SCHEME_DISPLAY_NAMES.get(scheme, scheme)
            self._show_theme_status(f"Theme applied: {used_backend} ({scheme_display}, {mode_str})")

            # Save theme settings
            self.settings.setValue("appearance/wallpaper", wallpaper)
            self.settings.setValue("appearance/scheme", scheme)
            self.settings.setValue("appearance/backend", backend)
            self.settings.setValue("appearance/theme_mode", self.theme_group.checkedId())
            self.settings.sync()

        except RuntimeError as e:
            self._show_theme_status(str(e), error=True)
        except Exception as e:
            self._show_theme_status(f"Error: {e}", error=True)

    def _show_theme_status(self, message: str, error: bool = False):
        """Update theme status label with message."""
        self.theme_status_label.setText(message)
        t = get_current_theme()
        if error:
            self.theme_status_label.setStyleSheet(f"color: {t.danger};")
        else:
            self.theme_status_label.setStyleSheet(f"color: {t.accent};")

        # Reset after 3 seconds
        from PySide6.QtCore import QTimer
        backend_info = get_backend_info()
        matugen_status = "installed" if backend_info["matugen"] else "not found"

        def reset():
            self.theme_status_label.setText(f"Matugen: {matugen_status}")
            self.theme_status_label.setStyleSheet("")

        QTimer.singleShot(3000, reset)

    # -------------------------------------------------------------------------
    # Settings Persistence
    # -------------------------------------------------------------------------

    
    def _get_bool(self, key: str, default: bool) -> bool:
        return cast(bool, self.settings.value(key, default, type=bool))

    def _get_str(self, key: str, default: str) -> str:
        return cast(str, self.settings.value(key, default, type=str))

    def _get_int(self, key: str, default: int) -> int:
        return cast(int, self.settings.value(key, default, type=int))

    def load_settings(self):
        """Load settings from persistent storage."""
        # General tab
        self.auto_start_cb.setChecked(self._get_bool("general/auto_start", False))
        self.remember_window_cb.setChecked(self._get_bool("general/remember_window", True))
        self.restore_session_cb.setChecked(self._get_bool("general/restore_session", True))
        self.language_combo.setCurrentText(self._get_str("general/language", "English"))
        self.date_format_combo.setCurrentText(self._get_str("general/date_format", "YYYY-MM-DD"))
        self.autosave_cb.setChecked(self._get_bool("general/autosave", True))
        self.autosave_spin.setValue(self._get_int("general/autosave_interval", 5))

        # Appearance tab - Theme settings
        theme_mode = cast(int, self.settings.value("appearance/theme_mode", 1, type=int))  # Default to Dark (1)
        if btn := self.theme_group.button(theme_mode):
            btn.setChecked(True)

        wallpaper = cast(str, self.settings.value("appearance/wallpaper", "", type=str))
        if wallpaper:
            self.wallpaper_path.setText(wallpaper)

        scheme = self.settings.value("appearance/scheme", "scheme-tonal-spot", str)
        for i in range(self.scheme_combo.count()):
            if self.scheme_combo.itemData(i) == scheme:
                self.scheme_combo.setCurrentIndex(i)
                break

        backend_id = {"auto": 0, "matugen": 1, "pillow": 2}.get(
            self._get_str("appearance/backend", "auto"), 0
        )

        if btn := self.backend_group.button(backend_id):
            btn.setChecked(True)

        self._update_scheme_state()

        # Appearance tab - Other settings
        self.scale_slider.setValue(self._get_int("appearance/scale", 100))
        self.font_combo.setCurrentText(self._get_str("appearance/font", "System Default"))
        self.font_size_spin.setValue(self._get_int("appearance/font_size", 11))
        self.animations_cb.setChecked(self._get_bool("appearance/animations", True))
        self.smooth_scroll_cb.setChecked(self._get_bool("appearance/smooth_scroll", True))

        # Advanced tab
        self.hardware_accel_cb.setChecked(self._get_bool("advanced/hardware_accel", True))
        self.gpu_rendering_cb.setChecked(self._get_bool("advanced/gpu_rendering", False))
        self.threads_spin.setValue(self._get_int("advanced/threads", 4))
        self.cache_spin.setValue(self._get_int("advanced/cache_size", 500))
        self.debug_mode_cb.setChecked(self._get_bool("advanced/debug_mode", False))
        self.verbose_logging_cb.setChecked(self._get_bool("advanced/verbose_logging", False))
        self.show_fps_cb.setChecked(self._get_bool("advanced/show_fps", False))

    def save_settings(self):
        """Save settings to persistent storage."""
        # General tab
        self.settings.setValue("general/auto_start", self.auto_start_cb.isChecked())
        self.settings.setValue("general/remember_window", self.remember_window_cb.isChecked())
        self.settings.setValue("general/restore_session", self.restore_session_cb.isChecked())
        self.settings.setValue("general/language", self.language_combo.currentText())
        self.settings.setValue("general/date_format", self.date_format_combo.currentText())
        self.settings.setValue("general/autosave", self.autosave_cb.isChecked())
        self.settings.setValue("general/autosave_interval", self.autosave_spin.value())

        # Appearance tab - Theme settings
        self.settings.setValue("appearance/theme_mode", self.theme_group.checkedId())
        self.settings.setValue("appearance/wallpaper", self.wallpaper_path.text())
        self.settings.setValue("appearance/scheme", self._get_selected_scheme())
        self.settings.setValue("appearance/backend", self._get_selected_backend())

        # Appearance tab - Other settings
        self.settings.setValue("appearance/scale", self.scale_slider.value())
        self.settings.setValue("appearance/font", self.font_combo.currentText())
        self.settings.setValue("appearance/font_size", self.font_size_spin.value())
        self.settings.setValue("appearance/animations", self.animations_cb.isChecked())
        self.settings.setValue("appearance/smooth_scroll", self.smooth_scroll_cb.isChecked())

        # Advanced tab
        self.settings.setValue("advanced/hardware_accel", self.hardware_accel_cb.isChecked())
        self.settings.setValue("advanced/gpu_rendering", self.gpu_rendering_cb.isChecked())
        self.settings.setValue("advanced/threads", self.threads_spin.value())
        self.settings.setValue("advanced/cache_size", self.cache_spin.value())
        self.settings.setValue("advanced/debug_mode", self.debug_mode_cb.isChecked())
        self.settings.setValue("advanced/verbose_logging", self.verbose_logging_cb.isChecked())
        self.settings.setValue("advanced/show_fps", self.show_fps_cb.isChecked())

        self.settings.sync()

    def apply_settings(self):
        """Apply and save settings."""
        self.save_settings()
        QMessageBox.information(self, "Settings Applied", "Settings have been saved successfully.")

    def accept_and_apply(self):
        """Apply settings and close dialog."""
        self.save_settings()
        self.close()

    def restore_defaults(self):
        """Restore all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore default settings?\nThis will reset all preferences.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Defaults Restored", "All settings have been restored to defaults.")

    def clear_cache(self):
        """Clear application cache."""
        QMessageBox.information(
            self,
            "Cache Cleared",
            f"Cache cleared successfully.\nFreed: {self.cache_spin.value()} MB",
        )


def main():
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
