"""PySide6 theming framework for modern Linux desktop applications.

Provides centralized dark theme with custom-styled widgets and Material You
color generation from wallpaper images.

Supports two color extraction backends:
- matugen: Full Material You with 9 scheme variants (requires external install)
- pillow: Built-in extraction with single algorithm

Usage:
    from glaze import generate_theme, Theme

    # Auto-detect best backend
    theme, backend = generate_theme(image_path="wallpaper.png")

    # With specific scheme (requires matugen)
    theme, backend = generate_theme(
        image_path="wallpaper.png",
        scheme="scheme-vibrant"
    )
"""

from glaze.theme import (
    Theme,
    theme,
    get_current_theme,
    set_current_theme,
    get_base_stylesheet,
    get_dialog_stylesheet,
    get_table_container_style,
)
from glaze.material_colors import (
    MaterialPalette,
    extract_dominant_color,
    generate_material_palette,
    palette_from_image,
    rgb_to_hex,
    hex_to_rgb,
    adjust_brightness,
    adjust_saturation,
    set_saturation,
    set_lightness,
    rotate_hue,
    blend_hue_towards_neutral,
)
from glaze.color_backend import (
    generate_theme,
    get_available_backend,
    get_backend_info,
    list_schemes,
    MATUGEN_SCHEMES,
    SCHEME_DISPLAY_NAMES,
)
from glaze.matugen import (
    is_matugen_available,
    generate_theme_from_matugen,
)

from importlib.metadata import version

__version__ = version("glaze")

__all__ = [
    # Theme core
    "Theme",
    "theme",
    "get_current_theme",
    "set_current_theme",
    "get_base_stylesheet",
    "get_dialog_stylesheet",
    "get_table_container_style",
    # Unified backend interface
    "generate_theme",
    "get_available_backend",
    "get_backend_info",
    "list_schemes",
    "MATUGEN_SCHEMES",
    "SCHEME_DISPLAY_NAMES",
    # Matugen backend
    "is_matugen_available",
    "generate_theme_from_matugen",
    # Pillow backend (material_colors)
    "MaterialPalette",
    "extract_dominant_color",
    "generate_material_palette",
    "palette_from_image",
    # Color utilities
    "rgb_to_hex",
    "hex_to_rgb",
    "adjust_brightness",
    "adjust_saturation",
    "set_saturation",
    "set_lightness",
    "rotate_hue",
    "blend_hue_towards_neutral",
]
