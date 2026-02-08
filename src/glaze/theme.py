"""Centralized theme configuration for PySide6 applications."""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

# Path to assets directory
_ASSETS_DIR = Path(__file__).parent / "assets"
_DOWN_ARROW_PATH = (_ASSETS_DIR / "down-arrow.svg").as_posix()

if TYPE_CHECKING:
    from .material_colors import MaterialPalette


@dataclass(frozen=True)
class Theme:
    # Background colors
    bg_primary: str = "#1a1a2e"
    bg_secondary: str = "#16213e"
    bg_tertiary: str = "#0f172a"

    # Surface colors
    surface: str = "#16213e"
    surface_variant: str = "#1e2a4a"
    surface_dim: str = "#0f172a"

    # Border colors
    border: str = "#0f3460"
    border_focus: str = "#e94560"
    border_hover: str = "#1e4d7b"
    outline: str = "#4a5568"
    outline_variant: str = "#2d3748"

    # Text colors
    text_primary: str = "#eee"
    text_secondary: str = "#888"
    text_tertiary: str = "#666"
    text_dark: str = "#333"
    text_disabled: str = "#555"

    # Accent colors (primary)
    accent: str = "#e94560"
    accent_hover: str = "#ff6b6b"
    accent_pressed: str = "#c73e54"
    accent_container: str = "#2d1520"
    accent_text: str = "#ffffff"       # Text on accent background
    accent_hover_text: str = "#ffffff" # Text on accent hover background

    # Secondary accent colors
    secondary: str = "#64b5f6"
    secondary_hover: str = "#90caf9"
    secondary_pressed: str = "#42a5f5"
    secondary_container: str = "#1a2f3a"

    # Tertiary accent colors
    tertiary: str = "#9c27b0"
    tertiary_hover: str = "#ba68c8"
    tertiary_pressed: str = "#8e24aa"
    tertiary_container: str = "#2a1a2e"

    # Status colors (kept static for consistency)
    success: str = "#4caf50"
    success_bg: str = "#e8f5e9"
    warning: str = "#ff9800"
    warning_bg: str = "#fff3e0"
    danger: str = "#d32f2f"
    danger_bg: str = "#ffebee"
    info: str = "#2196f3"
    info_bg: str = "#e3f2fd"

    # Misc
    selection_bg: str = "#e3f2fd"
    hover_overlay: str = "rgba(255, 255, 255, 0.05)"
    pressed_overlay: str = "rgba(0, 0, 0, 0.1)"
    border_radius: str = "8px"
    border_radius_sm: str = "6px"
    border_radius_lg: str = "12px"

    # Spacing
    spacing: int = 16
    spacing_sm: int = 8
    spacing_lg: int = 24
    spacing_xl: int = 32

    # Padding (for buttons, inputs, etc.)
    padding_v: int = 8   # Vertical padding
    padding_h: int = 14  # Horizontal padding
    padding_sm: int = 6  # Small padding
    padding_lg: int = 12 # Large padding

    # Table specific
    table_header_bg: str = "#1e2a4a"
    table_row_alt: str = "#1e2a4a"
    table_row_hover: str = "#253559"
    shadow_color: str = "rgba(0, 0, 0, 0.3)"
    shadow_elevation: str = "rgba(0, 0, 0, 0.2)"

    @classmethod
    def from_material_palette(cls, palette: "MaterialPalette") -> "Theme":
        """Create a Theme from a Material You palette.

        This method generates a comprehensive theme using Material You colors while
        keeping status colors (success, warning, danger, info) static for consistency.

        Args:
            palette: MaterialPalette generated from an image or source color

        Returns:
            Theme instance with colors mapped from the Material palette
        """
        from .material_colors import adjust_brightness, adjust_saturation

        return cls(
            # Background colors - from Material You
            bg_primary=palette.background,
            bg_secondary=palette.surface,
            bg_tertiary=adjust_brightness(palette.background, 0.8),

            # Surface colors - from Material You
            surface=palette.surface,
            surface_variant=palette.surface_variant,
            surface_dim=adjust_brightness(palette.surface, 0.85),

            # Border colors - from Material You
            border=palette.outline,
            border_focus=palette.primary,
            border_hover=adjust_brightness(palette.outline, 1.3),
            outline=palette.outline,
            outline_variant=adjust_brightness(palette.outline, 0.7),

            # Text colors - from Material You
            text_primary=palette.on_background,
            text_secondary=palette.on_surface_variant,
            text_tertiary=adjust_brightness(palette.on_surface_variant, 0.8),
            text_dark=palette.on_primary_container,
            text_disabled=adjust_brightness(palette.on_surface_variant, 0.5),

            # Primary accent colors - from Material You primary
            accent=palette.primary,
            accent_hover=adjust_brightness(palette.primary, 1.2),
            accent_pressed=adjust_brightness(palette.primary, 0.8),
            accent_container=palette.primary_container,
            accent_text=palette.on_primary,
            accent_hover_text=palette.on_primary,

            # Secondary accent colors - from Material You secondary
            secondary=palette.secondary,
            secondary_hover=adjust_brightness(palette.secondary, 1.2),
            secondary_pressed=adjust_brightness(palette.secondary, 0.8),
            secondary_container=palette.secondary_container,

            # Tertiary accent colors - from Material You tertiary
            tertiary=palette.tertiary,
            tertiary_hover=adjust_brightness(palette.tertiary, 1.2),
            tertiary_pressed=adjust_brightness(palette.tertiary, 0.8),
            tertiary_container=palette.tertiary_container,

            # Status colors - KEPT STATIC for functional consistency
            success="#4caf50",
            success_bg="#e8f5e9",
            warning="#ff9800",
            warning_bg="#fff3e0",
            danger="#d32f2f",
            danger_bg="#ffebee",
            info="#2196f3",
            info_bg="#e3f2fd",

            # Misc - from Material You
            selection_bg=palette.primary_container,
            hover_overlay="rgba(255, 255, 255, 0.05)",
            pressed_overlay="rgba(0, 0, 0, 0.1)",
            border_radius="8px",
            border_radius_sm="6px",
            border_radius_lg="12px",

            # Spacing (keep defaults)
            spacing=16,
            spacing_sm=8,
            spacing_lg=24,
            spacing_xl=32,

            # Padding
            padding_v=8,
            padding_h=14,
            padding_sm=6,
            padding_lg=12,

            # Table specific - from Material You
            table_header_bg=palette.surface_variant,
            table_row_alt=palette.surface_variant,
            table_row_hover=adjust_brightness(palette.surface_variant, 1.2),
            shadow_color="rgba(0, 0, 0, 0.3)",
            shadow_elevation="rgba(0, 0, 0, 0.2)",
        )


# Default theme instance
theme = Theme()


def get_current_theme() -> Theme:
    """Get the current active theme.

    This function looks up the theme from the module's global namespace,
    allowing for dynamic theme switching.

    Returns:
        The current Theme instance
    """
    return globals()['theme']


def set_current_theme(new_theme: Theme) -> None:
    """Set the current active theme.

    Args:
        new_theme: The Theme instance to set as current
    """
    globals()['theme'] = new_theme


def get_table_container_style(custom_theme: Theme | None = None) -> str:
    """Generate stylesheet for table container with shadow effect.

    Args:
        custom_theme: Optional custom theme to use. If None, uses current global theme.

    Returns:
        CSS stylesheet string
    """
    t = custom_theme or get_current_theme()
    return f"""
        QFrame#tableContainer {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: 12px;
        }}
    """


def _get_input_styles(t: Theme, variant: str = "base") -> str:
    """Generate shared input field styles (QLineEdit, QComboBox base).

    Args:
        t: Theme instance
        variant: "base" for main windows, "dialog" for dialogs (smaller, with min-height)

    Returns:
        CSS stylesheet string
    """
    if variant == "dialog":
        radius = t.border_radius_sm
        font_size = "13px"
        min_height = "min-height: 24px;"
        focus_bg = f"background-color: {t.bg_primary};"
        focus_border = t.accent
    else:
        radius = t.border_radius
        font_size = "14px"
        min_height = ""
        focus_bg = ""
        focus_border = t.border_focus

    return f"""
        QLineEdit, QComboBox {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: {radius};
            padding: {t.padding_v}px {t.padding_h}px;
            color: {t.text_primary};
            font-size: {font_size};
            {min_height}
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {focus_border};
            {focus_bg}
        }}
        QLineEdit:hover, QComboBox:hover {{
            border-color: {t.text_secondary};
        }}
    """


def _get_combobox_dropdown_styles(t: Theme) -> str:
    """Generate ComboBox dropdown/popup styles."""
    return f"""
        QComboBox::drop-down {{
            border: none;
            width: 30px;
            subcontrol-origin: padding;
            subcontrol-position: center right;
        }}
        QComboBox::down-arrow {{
            image: url({_DOWN_ARROW_PATH});
            width: 12px;
            height: 8px;
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {t.bg_secondary};
            color: {t.text_primary};
            selection-background-color: {t.accent};
            selection-color: {t.accent_text};
            border: 1px solid {t.border};
            border-radius: 4px;
            padding: 4px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            min-height: 24px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {t.table_row_hover};
        }}
        QComboBox QFrame {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: 4px;
            margin: 0;
            padding: 0;
        }}
    """


def _get_listview_styles(t: Theme, variant: str = "popup") -> str:
    """Generate QListView styles for ComboBox dropdowns.

    Args:
        t: Theme instance
        variant: "popup" for ThemedComboBox (no border), "standalone" for style_combobox (with border)

    Returns:
        CSS stylesheet string
    """
    border = "none" if variant == "popup" else f"1px solid {t.border}"
    padding = "0" if variant == "popup" else "4px"
    item_padding = "6px 10px" if variant == "popup" else "8px 12px"
    item_radius = "" if variant == "popup" else "border-radius: 4px;"

    return f"""
        QListView {{
            background-color: {t.bg_secondary};
            color: {t.text_primary};
            border: {border};
            border-radius: 4px;
            padding: {padding};
            outline: none;
            margin: 0;
        }}
        QListView::item {{
            padding: {item_padding};
            margin: 0;
            {item_radius}
        }}
        QListView::item:hover {{
            background-color: {t.table_row_hover};
        }}
        QListView::item:selected {{
            background-color: {t.accent};
            color: {t.accent_text};
        }}
    """


def _get_button_styles(t: Theme, variant: str = "base") -> str:
    """Generate shared button styles.

    Args:
        t: Theme instance
        variant: "base" for main windows, "dialog" for dialogs (smaller, refined)

    Returns:
        CSS stylesheet string
    """
    if variant == "dialog":
        radius = t.border_radius_sm
        font_size = "13px"
        font_weight = "600"
        secondary_bg = "transparent"
        secondary_hover_bg = f"background-color: {t.table_row_hover};"
        secondary_pressed = f"""
        QPushButton#secondary:pressed {{
            background-color: {t.bg_primary};
        }}"""
        danger_styles = ""
    else:
        radius = t.border_radius
        font_size = "14px"
        font_weight = "bold"
        secondary_bg = t.bg_secondary
        secondary_hover_bg = ""
        secondary_pressed = ""
        danger_styles = f"""
        QPushButton#danger {{
            background-color: transparent;
            border: 1px solid {t.danger};
            color: {t.danger};
        }}
        QPushButton#danger:hover {{
            background-color: {t.danger_bg};
        }}"""

    return f"""
        QPushButton {{
            background-color: {t.accent};
            color: {t.accent_text};
            border: none;
            border-radius: {radius};
            padding: {t.padding_v}px {t.padding_h}px;
            font-size: {font_size};
            font-weight: {font_weight};
        }}
        QPushButton:hover {{ background-color: {t.accent_hover}; color: {t.accent_hover_text}; }}
        QPushButton:pressed {{ background-color: {t.accent_pressed}; color: {t.accent_text}; }}
        QPushButton:disabled {{
            background-color: {t.border};
            color: {t.text_secondary};
        }}

        QPushButton#secondary {{
            background-color: {secondary_bg};
            border: 1px solid {t.border};
            color: {t.text_primary};
        }}
        QPushButton#secondary:hover {{
            border-color: {t.accent};
            color: {t.accent};
            {secondary_hover_bg}
        }}
        {secondary_pressed}
        {danger_styles}

        QPushButton#cancel {{
            background-color: transparent;
            border: 1px solid {t.border};
            color: {t.text_secondary};
        }}
        QPushButton#cancel:hover {{
            border-color: {t.text_primary};
            color: {t.text_primary};
            background-color: {t.table_row_hover};
        }}
    """


def _get_scrollbar_styles(t: Theme) -> str:
    """Generate scrollbar styles."""
    return f"""
        QScrollBar:vertical {{
            background: {t.bg_secondary};
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {t.border};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t.accent};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {t.bg_secondary};
            height: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t.border};
            border-radius: 5px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t.accent};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
    """


def get_base_stylesheet(custom_theme: Theme | None = None) -> str:
    """Generate base stylesheet for main windows.

    Args:
        custom_theme: Optional custom theme to use. If None, uses current global theme.

    Returns:
        CSS stylesheet string
    """
    t = custom_theme or get_current_theme()
    return f"""
        QMainWindow {{ background-color: {t.bg_primary}; }}
        QDialog {{ background-color: {t.bg_secondary}; }}

        QLabel {{ color: {t.text_primary}; }}
        QLabel#subtitle {{ color: {t.text_secondary}; font-size: 13px; }}

        {_get_input_styles(t)}
        {_get_combobox_dropdown_styles(t)}

        QTableWidget {{
            color: {t.text_primary};
            border: none;
            background: transparent;  /* Changed: let container show through */
            gridline-color: transparent;
            outline: none;
        }}
        QTableWidget::item {{
            background-color: {t.bg_secondary};
            padding: 12px 8px;
            border-bottom: 1px solid {t.border};
        }}
        QTableWidget::item:alternate {{
            background-color: {t.table_row_alt};
        }}
        QTableWidget::item:hover {{
            background-color: {t.table_row_hover};
        }}
        QTableWidget::item:selected {{
            background-color: {t.accent};
            color: {t.accent_text};
        }}
        QTableWidget::item:selected:hover {{
            background-color: {t.accent_hover};
            color: {t.accent_hover_text};
        }}

        /* Critical: Make header fully transparent for custom painting */
        QHeaderView {{
            background: transparent;
            border: none;
        }}

        QHeaderView::section {{
            background: transparent;
            border: none;
        }}

        /* Make table viewport transparent */
        QTableWidget QAbstractScrollArea {{
            background: transparent;
        }}

        QTableWidget QWidget {{
            background: transparent;
        }}

        {_get_scrollbar_styles(t)}
        {_get_button_styles(t)}
    """


def get_dialog_stylesheet(custom_theme: Theme | None = None) -> str:
    """Generate comprehensive stylesheet for dialogs with all widget types.
    
    Args:
        custom_theme: Optional custom theme to use. If None, uses current global theme.
        
    Returns:
        CSS stylesheet string
    """
    t = custom_theme or get_current_theme()
    return f"""
        QDialog {{
            background-color: {t.bg_primary};
            color: {t.text_primary};
        }}

        QLabel {{
            color: {t.text_secondary};
            font-size: 13px;
        }}

        /* Tab Widget - Clean integrated design */
        QTabWidget::pane {{
            background-color: {t.bg_secondary};
            border: none;
            border-radius: {t.border_radius};
            padding: 0;
        }}
        QTabBar {{
            background-color: transparent;
            border: none;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {t.text_secondary};
            border: none;
            border-bottom: 2px solid transparent;
            padding: 12px 20px;
            margin-right: 8px;
            margin-bottom: 0px;
            font-size: 13px;
            font-weight: 500;
            outline: none;
        }}
        QTabBar::tab:selected {{
            color: {t.text_primary};
            border-bottom: 2px solid {t.accent};
        }}
        QTabBar::tab:hover:!selected {{
            color: {t.text_primary};
        }}

        /* Group Box - Simple clean style */
        QGroupBox {{
            background-color: {t.bg_primary};
            border: 1px solid {t.border};
            border-radius: {t.border_radius};
            margin-top: 20px;
            padding: {t.spacing_lg}px {t.spacing}px {t.spacing}px {t.spacing}px;
            font-size: 13px;
        }}
        QGroupBox::title {{
            color: {t.text_primary};
            font-weight: 600;
            font-size: 14px;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            left: 10px;
        }}

        /* CheckBox - Modern style */
        QCheckBox {{
            color: {t.text_primary};
            spacing: 10px;
            font-size: 13px;
            padding: 4px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {t.border};
            border-radius: 4px;
            background-color: {t.bg_primary};
        }}
        QCheckBox::indicator:checked {{
            background-color: {t.accent};
            border-color: {t.accent};
            image: none;
        }}
        QCheckBox::indicator:hover {{
            border-color: {t.accent};
            background-color: {t.table_row_hover};
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {t.accent_hover};
        }}

        /* RadioButton - Modern style */
        QRadioButton {{
            color: {t.text_primary};
            spacing: 10px;
            font-size: 13px;
            padding: 4px;
        }}
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {t.border};
            border-radius: 10px;
            background-color: {t.bg_primary};
        }}
        QRadioButton::indicator:checked {{
            background-color: {t.accent};
            border-color: {t.accent};
        }}
        QRadioButton::indicator:hover {{
            border-color: {t.accent};
            background-color: {t.table_row_hover};
        }}
        QRadioButton::indicator:checked:hover {{
            background-color: {t.accent_hover};
        }}

        /* SpinBox - Polished style */
        QSpinBox {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: {t.border_radius_sm};
            padding: {t.padding_v}px {t.padding_h}px;
            color: {t.text_primary};
            font-size: 13px;
            min-height: 24px;
        }}
        QSpinBox:focus {{
            border: 1px solid {t.accent};
            background-color: {t.bg_primary};
        }}
        QSpinBox:hover {{
            border-color: {t.text_secondary};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: transparent;
            border: none;
            width: 20px;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {t.table_row_hover};
        }}

        /* Slider - Modern flat style */
        QSlider::groove:horizontal {{
            background: {t.border};
            height: 4px;
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {t.accent};
            width: 18px;
            height: 18px;
            margin: -7px 0;
            border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {t.accent_hover};
            width: 20px;
            height: 20px;
            margin: -8px 0;
        }}
        QSlider::sub-page:horizontal {{
            background: {t.accent};
            border-radius: 2px;
        }}
        QSlider::add-page:horizontal {{
            background: {t.border};
            border-radius: 2px;
        }}

        /* ComboBox - Clean modern style */
        QComboBox {{
            background-color: {t.bg_secondary};
            border: 1px solid {t.border};
            border-radius: {t.border_radius_sm};
            padding: {t.padding_v}px {t.padding_h}px;
            color: {t.text_primary};
            font-size: 13px;
            min-height: 24px;
        }}
        QComboBox:focus {{
            border: 1px solid {t.accent};
            background-color: {t.bg_primary};
        }}
        QComboBox:hover {{
            border-color: {t.text_secondary};
        }}
        {_get_combobox_dropdown_styles(t)}

        /* Input fields - use shared styles */
        {_get_input_styles(t, variant="dialog")}

        /* Buttons - use shared styles */
        {_get_button_styles(t, variant="dialog")}
    """
