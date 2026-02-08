"""Matugen CLI wrapper for Material You color generation.

This module provides an interface to the matugen tool for generating
Material You color schemes from wallpaper images or hex colors.

Matugen provides scheme variants not available in the Pillow-based extractor:
- scheme-tonal-spot (default)
- scheme-vibrant
- scheme-expressive
- scheme-rainbow
- scheme-fruit-salad
- scheme-fidelity
- scheme-content
- scheme-monochrome
- scheme-neutral

Install matugen:
    Arch: paru -S matugen-bin
    Cargo: cargo install matugen
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .theme import Theme

# Available matugen color schemes
MATUGEN_SCHEMES = [
    "scheme-tonal-spot",    # Default Material You, balanced tones
    "scheme-vibrant",       # Higher saturation, punchy colors
    "scheme-expressive",    # Bold, high contrast
    "scheme-rainbow",       # Tertiary shifts through hues
    "scheme-fruit-salad",   # Playful, varied palette
    "scheme-fidelity",      # Stays close to source color
    "scheme-content",       # Optimized for content-heavy UIs
    "scheme-monochrome",    # Grayscale with subtle tint
    "scheme-neutral",       # Muted, professional
]

# Display names for UI
SCHEME_DISPLAY_NAMES = {
    "scheme-tonal-spot": "Tonal Spot (Default)",
    "scheme-vibrant": "Vibrant",
    "scheme-expressive": "Expressive",
    "scheme-rainbow": "Rainbow",
    "scheme-fruit-salad": "Fruit Salad",
    "scheme-fidelity": "Fidelity",
    "scheme-content": "Content",
    "scheme-monochrome": "Monochrome",
    "scheme-neutral": "Neutral",
}


def is_matugen_available() -> bool:
    """Check if matugen is installed and available in PATH.

    Returns:
        True if matugen is available, False otherwise
    """
    return shutil.which("matugen") is not None


def get_matugen_colors(
    image_path: str | None = None,
    color: str | None = None,
    scheme: str = "scheme-tonal-spot",
    dark_mode: bool = True,
) -> dict[str, str]:
    """Get raw color dictionary from matugen.

    Args:
        image_path: Path to wallpaper image
        color: Hex color string (e.g., "#e94560")
        scheme: Matugen scheme name
        dark_mode: Whether to extract dark mode colors

    Returns:
        Dictionary mapping color names to hex values

    Raises:
        ValueError: If neither image_path nor color provided
        RuntimeError: If matugen is not installed
        subprocess.CalledProcessError: If matugen command fails
    """
    if not image_path and not color:
        raise ValueError("Must provide either image_path or color")

    if not is_matugen_available():
        raise RuntimeError(
            "matugen is not installed. Install with: paru -S matugen-bin "
            "or cargo install matugen"
        )

    mode = "dark" if dark_mode else "light"

    if image_path:
        cmd = [
            "matugen", "image", str(image_path),
            "-t", scheme,
            "-m", mode,
            "-j", "hex"
        ]
    else:
        hex_color = color if color.startswith("#") else f"#{color}"
        cmd = [
            "matugen", "color", "hex", hex_color,
            "-t", scheme,
            "-m", mode,
            "-j", "hex"
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)

    # Matugen returns {color_name: {dark: hex, light: hex, default: hex}}
    return {k: v[mode] for k, v in data["colors"].items()}


def generate_theme_from_matugen(
    image_path: str | None = None,
    color: str | None = None,
    scheme: str = "scheme-tonal-spot",
    dark_mode: bool = True,
) -> "Theme":
    """Generate a Theme using matugen for color extraction.

    Args:
        image_path: Path to wallpaper image
        color: Hex color string (e.g., "#e94560")
        scheme: Matugen scheme name (see MATUGEN_SCHEMES)
        dark_mode: Whether to generate dark mode theme

    Returns:
        Theme instance with colors from matugen

    Raises:
        ValueError: If neither image_path nor color provided
        RuntimeError: If matugen is not installed
    """
    from .theme import Theme

    c = get_matugen_colors(image_path, color, scheme, dark_mode)

    # Background colors depend on mode:
    # - Dark mode: OLED black base like Ax-Shell
    # - Light mode: Use actual surface colors from matugen
    if dark_mode:
        bg_primary = "#000000"                        # Pure OLED black
        bg_secondary = c["surface_container_lowest"]  # Slightly elevated
        bg_tertiary = c["surface_container_low"]      # Cards, panels
        surface_dim = "#000000"
        hover_overlay = "rgba(255, 255, 255, 0.05)"
        pressed_overlay = "rgba(0, 0, 0, 0.1)"
    else:
        # Light mode uses actual surface colors
        bg_primary = c["surface"]                     # Light background
        bg_secondary = c["surface_container_lowest"]  # Slightly dimmer
        bg_tertiary = c["surface_container_low"]      # Cards, panels
        surface_dim = c["surface_dim"]
        hover_overlay = "rgba(0, 0, 0, 0.05)"
        pressed_overlay = "rgba(0, 0, 0, 0.1)"

    return Theme(
        # === Background colors ===
        bg_primary=bg_primary,
        bg_secondary=bg_secondary,
        bg_tertiary=bg_tertiary,

        # === Surface colors (for elevated elements) ===
        surface=c["surface_container_low"],
        surface_variant=c["surface_container"],
        surface_dim=surface_dim,

        # === Border colors ===
        border=c["outline_variant"],
        border_focus=c["primary"],
        border_hover=c["outline"],
        outline=c["outline"],
        outline_variant=c["outline_variant"],

        # === Text colors ===
        text_primary=c["on_surface"],
        text_secondary=c["on_surface_variant"],
        text_tertiary=c["outline"],
        text_dark=c["on_primary_container"],     # Text on accent/button backgrounds
        text_disabled=c["outline_variant"],

        # === Primary accent colors ===
        # Using tonal button style:
        # - Normal: primary_container bg + on_primary_container text
        # - Hover: primary bg + on_primary text (strong feedback)
        accent=c["primary_container"],           # Button background
        accent_hover=c["primary"],               # Hover: stronger accent
        accent_pressed=c["primary_container"],   # Pressed: back to container
        accent_container=c["primary_container"],
        accent_text=c["on_primary_container"],   # Text on button
        accent_hover_text=c["on_primary"],       # Text on hover bg

        # === Secondary accent colors ===
        secondary=c["secondary"],
        secondary_hover=c["secondary_fixed_dim"],
        secondary_pressed=c["secondary_container"],
        secondary_container=c["secondary_container"],

        # === Tertiary accent colors ===
        tertiary=c["tertiary"],
        tertiary_hover=c["tertiary_fixed_dim"],
        tertiary_pressed=c["tertiary_container"],
        tertiary_container=c["tertiary_container"],

        # === Status colors (use matugen semantic colors) ===
        success="#4caf50",
        success_bg="#e8f5e9",
        warning="#ff9800",
        warning_bg="#fff3e0",
        danger=c["error"],
        danger_bg=c["error_container"],
        info="#2196f3",
        info_bg="#e3f2fd",

        # === Selection/highlighting ===
        selection_bg=c["primary_container"],
        hover_overlay=hover_overlay,
        pressed_overlay=pressed_overlay,

        # === Table specific ===
        table_header_bg=c["surface_container"],
        table_row_alt=c["surface_container_lowest"],
        table_row_hover=c["surface_container_low"],
        shadow_color=c["shadow"],
        shadow_elevation=c["scrim"],

        # === Spacing and radius (keep defaults) ===
        border_radius="8px",
        border_radius_sm="6px",
        border_radius_lg="12px",
        spacing=16,
        spacing_sm=8,
        spacing_lg=24,
        spacing_xl=32,
        padding_v=8,
        padding_h=14,
        padding_sm=6,
        padding_lg=12,
    )


def normalize_scheme_name(scheme: str) -> str:
    """Normalize scheme name to full matugen format.

    Accepts both short names (e.g., "vibrant") and full names
    (e.g., "scheme-vibrant").

    Args:
        scheme: Scheme name in short or full format

    Returns:
        Full scheme name (e.g., "scheme-vibrant")

    Raises:
        ValueError: If scheme name is not recognized
    """
    # Already in full format
    if scheme in MATUGEN_SCHEMES:
        return scheme

    # Try adding prefix
    full_name = f"scheme-{scheme}"
    if full_name in MATUGEN_SCHEMES:
        return full_name

    valid_schemes = ", ".join(MATUGEN_SCHEMES)
    raise ValueError(
        f"Unknown scheme '{scheme}'. Valid schemes: {valid_schemes}"
    )
