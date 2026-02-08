"""Material You color generation from images.

This module provides utilities to extract dominant colors from wallpaper images
and generate Material You-inspired color schemes for the Glaze theme system.
"""

from dataclasses import dataclass
from typing import Tuple, List
import colorsys


@dataclass
class MaterialPalette:
    """Material You color palette extracted from an image."""

    # Primary colors (main accent)
    primary: str
    primary_container: str
    on_primary: str
    on_primary_container: str

    # Secondary colors (complementary)
    secondary: str
    secondary_container: str
    on_secondary: str
    on_secondary_container: str

    # Tertiary colors (accent variation)
    tertiary: str
    tertiary_container: str
    on_tertiary: str
    on_tertiary_container: str

    # Background colors
    background: str
    on_background: str
    surface: str
    on_surface: str
    surface_variant: str
    on_surface_variant: str

    # Utility colors
    error: str
    on_error: str
    outline: str
    shadow: str


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        Hex color string (e.g., "#ff5733")
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    """Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#ff5733" or "ff5733")

    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def adjust_brightness(hex_color: str, factor: float) -> str:
    """Adjust the brightness of a color.

    Args:
        hex_color: Hex color string
        factor: Brightness adjustment factor (>1 brightens, <1 darkens)

    Returns:
        Adjusted hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def adjust_saturation(hex_color: str, factor: float) -> str:
    """Adjust the saturation of a color.

    Args:
        hex_color: Hex color string
        factor: Saturation adjustment factor (>1 increases, <1 decreases)

    Returns:
        Adjusted hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    s = max(0, min(1, s * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def set_saturation(hex_color: str, saturation: float) -> str:
    """Set absolute saturation level of a color.

    Args:
        hex_color: Hex color string
        saturation: Target saturation (0.0 to 1.0)

    Returns:
        Adjusted hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    s = max(0, min(1, saturation))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def set_lightness(hex_color: str, lightness: float) -> str:
    """Set absolute lightness level of a color.

    Args:
        hex_color: Hex color string
        lightness: Target lightness (0.0 to 1.0)

    Returns:
        Adjusted hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = max(0, min(1, lightness))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def blend_hue_towards_neutral(hex_color: str, neutral_hue: float, blend_factor: float) -> str:
    """Blend a color's hue towards a neutral hue.

    Args:
        hex_color: Source hex color string
        neutral_hue: Target neutral hue (0.0 to 1.0, e.g., 0.65 for blue)
        blend_factor: How much to blend (0.0 = no change, 1.0 = fully neutral)

    Returns:
        Blended hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)

    # Blend hue towards neutral
    h = h * (1 - blend_factor) + neutral_hue * blend_factor

    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def rotate_hue(hex_color: str, degrees: float) -> str:
    """Rotate the hue of a color.

    Args:
        hex_color: Hex color string
        degrees: Degrees to rotate hue (0-360)

    Returns:
        Rotated hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    h = (h + degrees/360) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def get_contrasting_text(hex_color: str) -> str:
    """Get contrasting text color (black or white) for a background color.

    Args:
        hex_color: Background hex color string

    Returns:
        "#ffffff" for dark backgrounds, "#000000" for light backgrounds
    """
    r, g, b = hex_to_rgb(hex_color)
    # Calculate relative luminance (WCAG formula)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#ffffff"


def extract_dominant_color(image_path: str, sample_size: int = 150) -> str:
    """Extract the dominant color from an image.

    Args:
        image_path: Path to the image file
        sample_size: Size to resize image for color analysis (smaller = faster)

    Returns:
        Hex color string of the dominant color

    Raises:
        ImportError: If PIL/Pillow is not installed
        FileNotFoundError: If image file doesn't exist
    """
    try:
        from PIL import Image
        from PIL.Image import core as Imaging
    except ImportError:
        raise ImportError(
            "Pillow is required for image color extraction. "
            "Install it with: pip install pillow"
        )

    # Load and resize image for faster processing
    img = Image.open(image_path)
    img = img.convert('RGB')
    img.thumbnail((sample_size, sample_size))

    # Get color histogram
    pixels: Imaging.ImagingCore = img.getdata()

    # Find dominant color using color quantization
    from collections import Counter

    # Group similar colors (reduce precision to avoid too many unique colors)
    def simplify_color(rgb):
        # Round to nearest 32 to group similar colors
        return tuple((c // 32) * 32 for c in rgb)

    simplified_pixels = [simplify_color(p) for p in pixels]
    color_counts = Counter(simplified_pixels)

    # Get most common color
    dominant_rgb = color_counts.most_common(1)[0][0]

    return rgb_to_hex(*dominant_rgb)


def generate_material_palette(source_color: str, dark_mode: bool = True) -> MaterialPalette:
    """Generate a complete Material You palette from a source color.

    Uses proper color theory to create harmonious schemes inspired by the default theme.
    Backgrounds are kept in cool neutral range (blue-purple) with subtle tints.

    Args:
        source_color: Hex color string to base the palette on
        dark_mode: Whether to generate dark mode colors (default: True)

    Returns:
        MaterialPalette with complete color scheme
    """
    # Extract source color properties
    r, g, b = hex_to_rgb(source_color)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)

    # DARK MODE PALETTE
    if dark_mode:
        # === PRIMARY ACCENT ===
        # Ensure vibrant accent with proper saturation and lightness
        primary = set_saturation(source_color, max(0.6, s))  # At least 60% saturation
        primary = set_lightness(primary, max(0.45, min(0.60, l)))  # 45-60% lightness
        
        primary_container = set_lightness(primary, 0.18)  # Dark container
        primary_container = set_saturation(primary_container, 0.5)
        on_primary = "#000000"
        on_primary_container = set_lightness(primary, 0.85)

        # === SECONDARY ACCENT (Analogous +60°) ===
        secondary = rotate_hue(primary, 60)
        secondary = set_saturation(secondary, 0.65)
        secondary = set_lightness(secondary, 0.55)
        
        secondary_container = set_lightness(secondary, 0.16)
        secondary_container = set_saturation(secondary_container, 0.45)
        on_secondary = "#000000"
        on_secondary_container = set_lightness(secondary, 0.85)

        # === TERTIARY ACCENT (Split-complementary -60°) ===
        tertiary = rotate_hue(primary, -60)
        tertiary = set_saturation(tertiary, 0.70)
        tertiary = set_lightness(tertiary, 0.58)
        
        tertiary_container = set_lightness(tertiary, 0.17)
        tertiary_container = set_saturation(tertiary_container, 0.48)
        on_tertiary = "#000000"
        on_tertiary_container = set_lightness(tertiary, 0.85)

        # === BACKGROUNDS (Cool Neutral Base) ===
        # Use blue-purple neutral (0.63 hue) as base, blend with primary
        NEUTRAL_HUE = 0.63  # Blue-purple (like default #1a1a2e)
        bg_hue_blend = blend_hue_towards_neutral(primary, NEUTRAL_HUE, 0.7)
        
        background = set_saturation(bg_hue_blend, 0.08)
        background = set_lightness(background, 0.11)
        on_background = "#e6e6e6"

        surface = set_saturation(bg_hue_blend, 0.10)
        surface = set_lightness(surface, 0.14)
        on_surface = "#e6e6e6"

        surface_variant = blend_hue_towards_neutral(primary, NEUTRAL_HUE, 0.5)
        surface_variant = set_saturation(surface_variant, 0.22)
        surface_variant = set_lightness(surface_variant, 0.16)
        on_surface_variant = "#c4c4c4"

        # === UTILITY COLORS ===
        error = "#cf6679"
        on_error = "#000000"
        outline = set_saturation(primary, 0.35)
        outline = set_lightness(outline, 0.28)
        shadow = "#000000"

    else:
        # LIGHT MODE PALETTE
        primary = set_saturation(source_color, max(0.7, s))
        primary = set_lightness(primary, max(0.40, min(0.55, l)))
        
        primary_container = set_lightness(primary, 0.85)
        primary_container = set_saturation(primary_container, 0.4)
        on_primary = "#ffffff"
        on_primary_container = set_lightness(primary, 0.20)

        secondary = rotate_hue(primary, 60)
        secondary = set_saturation(secondary, 0.65)
        secondary = set_lightness(secondary, 0.48)
        
        secondary_container = set_lightness(secondary, 0.88)
        secondary_container = set_saturation(secondary_container, 0.35)
        on_secondary = "#ffffff"
        on_secondary_container = set_lightness(secondary, 0.18)

        tertiary = rotate_hue(primary, -60)
        tertiary = set_saturation(tertiary, 0.70)
        tertiary = set_lightness(tertiary, 0.50)
        
        tertiary_container = set_lightness(tertiary, 0.90)
        tertiary_container = set_saturation(tertiary_container, 0.32)
        on_tertiary = "#ffffff"
        on_tertiary_container = set_lightness(tertiary, 0.16)

        # Light mode backgrounds - very subtle tint
        NEUTRAL_HUE_LIGHT = 0.55  # Slightly warmer for light mode
        bg_hue_blend = blend_hue_towards_neutral(primary, NEUTRAL_HUE_LIGHT, 0.85)
        
        background = set_saturation(bg_hue_blend, 0.02)
        background = set_lightness(background, 0.98)
        on_background = "#1a1a1a"

        surface = set_saturation(bg_hue_blend, 0.03)
        surface = set_lightness(surface, 0.95)
        on_surface = "#1a1a1a"

        surface_variant = blend_hue_towards_neutral(primary, NEUTRAL_HUE_LIGHT, 0.75)
        surface_variant = set_saturation(surface_variant, 0.08)
        surface_variant = set_lightness(surface_variant, 0.90)
        on_surface_variant = "#4a4a4a"

        error = "#b00020"
        on_error = "#ffffff"
        outline = set_saturation(primary, 0.30)
        outline = set_lightness(outline, 0.55)
        shadow = "#000000"

    return MaterialPalette(
        primary=primary,
        primary_container=primary_container,
        on_primary=on_primary,
        on_primary_container=on_primary_container,
        secondary=secondary,
        secondary_container=secondary_container,
        on_secondary=on_secondary,
        on_secondary_container=on_secondary_container,
        tertiary=tertiary,
        tertiary_container=tertiary_container,
        on_tertiary=on_tertiary,
        on_tertiary_container=on_tertiary_container,
        background=background,
        on_background=on_background,
        surface=surface,
        on_surface=on_surface,
        surface_variant=surface_variant,
        on_surface_variant=on_surface_variant,
        error=error,
        on_error=on_error,
        outline=outline,
        shadow=shadow,
    )



def palette_from_image(image_path: str, dark_mode: bool = True) -> MaterialPalette:
    """Generate a Material You palette directly from an image.

    Convenience function that extracts the dominant color and generates
    a complete palette in one step.

    Args:
        image_path: Path to the wallpaper image
        dark_mode: Whether to generate dark mode colors (default: True)

    Returns:
        MaterialPalette based on the image's dominant color
    """
    dominant_color = extract_dominant_color(image_path)
    return generate_material_palette(dominant_color, dark_mode=dark_mode)
