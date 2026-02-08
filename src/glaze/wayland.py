"""Wayland/Hyprland/Cosmic compatibility utilities for PySide6 applications.

This module provides helper functions to ensure PySide6 windows work properly
with various Linux desktop environments and window managers, including:
- Tiling WMs: Hyprland, Sway, i3, bspwm, awesome, dwm, xmonad, qtile
- Stacking DEs: COSMIC, GNOME, KDE Plasma
- Wayland compositors with proper resize/move support
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


def is_wayland() -> bool:
    """Detect if running under a Wayland session.

    Returns:
        True if Wayland is detected, False otherwise
    """
    # Check for Wayland display
    if os.environ.get("WAYLAND_DISPLAY"):
        return True

    # Check XDG session type
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland":
        return True

    return False


def is_cosmic() -> bool:
    """Detect if running under COSMIC desktop environment (Pop!_OS).

    COSMIC is System76's Rust-based desktop environment, introduced in
    Pop!_OS 24.04. It's a stacking/floating compositor with optional
    auto-tiling features.

    Returns:
        True if COSMIC is detected, False otherwise
    """
    # Check XDG_CURRENT_DESKTOP
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    if current_desktop == "COSMIC":
        return True

    # Check XDG_SESSION_DESKTOP
    session_desktop = os.environ.get("XDG_SESSION_DESKTOP", "").upper()
    if session_desktop == "COSMIC":
        return True

    # Check for COSMIC-specific environment variables
    cosmic_vars = [
        "COSMIC_PANEL_NAME",
        "COSMIC_PANEL_SIZE",
        "COSMIC_PANEL_ANCHOR",
    ]
    for var in cosmic_vars:
        if os.environ.get(var):
            return True

    return False


def is_hyprland() -> bool:
    """Detect if running under Hyprland window manager.

    Returns:
        True if Hyprland is detected, False otherwise
    """
    # Check for Hyprland-specific environment variables
    hyprland_instance = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if hyprland_instance:
        return True

    # Check XDG_CURRENT_DESKTOP
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "hyprland" in current_desktop:
        return True

    # Check session type
    session_desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    if "hyprland" in session_desktop:
        return True

    return False


def is_tiling_wm() -> bool:
    """Detect if running under a pure tiling window manager.

    Note: COSMIC is NOT considered a tiling WM here, even though it has
    auto-tiling features. COSMIC is a stacking compositor that should be
    treated like GNOME/KDE for window attribute purposes. Use
    is_cosmic_autotile_enabled() to check for COSMIC's tiling mode.

    Returns:
        True if a pure tiling WM is detected, False otherwise
    """
    if is_hyprland():
        return True

    # Check for other common tiling WMs
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session_desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()

    tiling_wms = ["i3", "sway", "bspwm", "awesome", "dwm", "xmonad", "qtile"]

    for wm in tiling_wms:
        if wm in current_desktop or wm in session_desktop:
            return True

    return False


def is_stacking_de() -> bool:
    """Detect if running under a stacking/floating desktop environment.

    Stacking DEs include COSMIC, GNOME, KDE Plasma, XFCE, Cinnamon, etc.
    These DEs typically don't require special X11 window type hints.

    Returns:
        True if a stacking DE is detected, False otherwise
    """
    if is_cosmic():
        return True

    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session_desktop = os.environ.get("XDG_SESSION_DESKTOP", "").lower()
    desktop_session = os.environ.get("DESKTOP_SESSION", "").lower()

    stacking_des = [
        "gnome", "kde", "plasma", "xfce", "cinnamon", "mate",
        "lxde", "lxqt", "budgie", "pantheon", "deepin", "unity"
    ]

    for de in stacking_des:
        if de in current_desktop or de in session_desktop or de in desktop_session:
            return True

    return False


def get_desktop_environment() -> str:
    """Get the name of the current desktop environment or window manager.

    Returns:
        Name of the detected DE/WM, or "unknown" if not detected
    """
    if is_cosmic():
        return "COSMIC"
    if is_hyprland():
        return "Hyprland"

    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
    if current_desktop:
        return current_desktop

    session_desktop = os.environ.get("XDG_SESSION_DESKTOP", "")
    if session_desktop:
        return session_desktop

    return "unknown"


def setup_hyprland_window(window: QWidget):
    """Configure a QWidget/QMainWindow for optimal tiling WM compatibility.

    This ensures:
    - Super+MB1 (left mouse) can move windows
    - Super+MB2 (right mouse) can resize windows
    - Proper tiling behavior
    - Floating window support

    Note: This creates a frameless window. For windows with native
    decorations, use setup_window_decorated() instead.

    Args:
        window: The QWidget or QMainWindow to configure
    """
    # Set window flags for proper Wayland/X11 behavior
    # Qt.Window makes it a top-level window
    window.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.FramelessWindowHint  # Remove if you want native decorations
    )

    # Enable mouse tracking for WM's window management
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
    window.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    # Ensure the window can be moved and resized by the WM
    window.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeCombo, True)


def setup_window_decorated(window: QWidget):
    """Configure a QWidget/QMainWindow with native window decorations.

    Use this if you want the default title bar and borders. Automatically
    detects the desktop environment and applies appropriate settings:

    - Tiling WMs (Hyprland, i3, sway, etc.): Applies X11 window type hints
    - Stacking DEs (COSMIC, GNOME, KDE): Skips hints to avoid interference

    Args:
        window: The QWidget or QMainWindow to configure
    """
    # Just set it as a normal window - let the WM/DE handle decorations
    window.setWindowFlags(Qt.WindowType.Window)

    # Only apply X11 hints on tiling window managers
    # On stacking DEs like COSMIC/GNOME/KDE, this can interfere with window management
    if is_tiling_wm():
        window.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeCombo, True)


# Alias for backwards compatibility
setup_hyprland_window_decorated = setup_window_decorated


def make_window_floating(window: QWidget, width: int, height: int):
    """Configure a window to float by default.

    Works with tiling WMs (Hyprland, i3, sway) and stacking DEs (COSMIC, GNOME, KDE).
    Sets size constraints that hint to the WM/DE that this window prefers floating.

    Args:
        window: The QWidget or QMainWindow to configure
        width: Preferred width
        height: Preferred height
    """
    setup_window_decorated(window)

    # Set size hints to suggest floating
    window.setMinimumSize(width // 2, height // 2)
    window.setMaximumSize(width * 2, height * 2)
    window.resize(width, height)


def make_window_tiled(window: QWidget):
    """Configure a window for tiling/maximized layouts.

    Works with tiling WMs (Hyprland, i3, sway) and stacking DEs (COSMIC, GNOME, KDE).
    Removes size constraints to allow full tiling or maximization.

    Args:
        window: The QWidget or QMainWindow to configure
    """
    setup_window_decorated(window)

    # Remove size constraints to allow full tiling
    window.setMinimumSize(400, 300)
    window.setMaximumSize(16777215, 16777215)  # Qt's QWIDGETSIZE_MAX


def hyprctl_float_active():
    """Use hyprctl to float the currently active window on Hyprland.

    This is called automatically after show() when using FramelessMainWindow.
    Can also be called manually if needed.
    """
    if not is_hyprland():
        return

    import subprocess
    try:
        # Float the active window using hyprctl
        subprocess.run(
            ["hyprctl", "dispatch", "setfloating", "active"],
            capture_output=True,
            timeout=1
        )
    except Exception:
        pass  # Silently fail if hyprctl not available


def make_window_frameless(window: QWidget, width: int = 0, height: int = 0, floating: bool = True):
    """Configure a window as frameless for custom decorations.

    Use this when you want to provide your own title bar using the TitleBar widget.
    The window will have no system decorations, allowing full theme integration.

    Args:
        window: The QWidget or QMainWindow to configure
        width: Optional preferred width (0 = no constraint)
        height: Optional preferred height (0 = no constraint)
        floating: If True (default), hint to tiling WMs that window should float

    Example:
        from glaze.wayland import make_window_frameless
        from glaze.widgets import TitleBar

        class MyWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                make_window_frameless(self, 400, 300)

                central = QWidget()
                layout = QVBoxLayout(central)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)

                self.title_bar = TitleBar(self, "My App")
                layout.addWidget(self.title_bar)

                # Add your content...
                self.setCentralWidget(central)
    """
    # Set frameless window flags
    window.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.FramelessWindowHint
    )

    # Enable transparency for rounded corners
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    # Set size constraints
    if width > 0 and height > 0:
        window.resize(width, height)
        window.setMinimumSize(width // 2, height // 2)
        if floating:
            window.setMaximumSize(width * 2, height * 2)

    # Store floating preference for later use by showEvent
    window.setProperty("_glaze_floating", floating)