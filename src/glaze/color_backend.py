"""Unified color backend interface for theme generation.

This module provides a single entry point for generating themes from
wallpaper images or hex colors, automatically selecting the best
available backend (matugen or pillow).

Usage:
    from glaze.color_backend import generate_theme

    # Auto-detect backend
    theme, backend = generate_theme(image_path="wallpaper.png")

    # Force specific backend
    theme, backend = generate_theme(
        image_path="wallpaper.png",
        scheme="scheme-vibrant",
        backend="matugen"
    )

    # From hex color
    theme, backend = generate_theme(color="#e94560")
"""

from __future__ import annotations

import warnings
from typing import Literal

from .theme import Theme, set_current_theme
from .matugen import (
    is_matugen_available,
    generate_theme_from_matugen,
    normalize_scheme_name,
    MATUGEN_SCHEMES,
    SCHEME_DISPLAY_NAMES,
)
from .material_colors import palette_from_image, generate_material_palette

# Type alias for backend selection
Backend = Literal["auto", "matugen", "pillow"]


def get_available_backend() -> str:
    """Return the best available backend.

    Returns:
        "matugen" if installed, otherwise "pillow"
    """
    return "matugen" if is_matugen_available() else "pillow"


def get_backend_info() -> dict[str, bool]:
    """Get availability status of all backends.

    Returns:
        Dictionary with backend names as keys and availability as values
    """
    return {
        "matugen": is_matugen_available(),
        "pillow": True,  # Always available (bundled dependency)
    }


def generate_theme(
    image_path: str | None = None,
    color: str | None = None,
    scheme: str = "scheme-tonal-spot",
    dark_mode: bool = True,
    backend: Backend = "auto",
) -> tuple[Theme, str]:
    """Generate a theme from an image or color.

    This is the main entry point for theme generation. It automatically
    selects the best available backend or uses the one specified.

    Args:
        image_path: Path to wallpaper image
        color: Hex color string (e.g., "#e94560")
        scheme: Color scheme variant (matugen only, see MATUGEN_SCHEMES)
        dark_mode: Whether to generate dark mode theme
        backend: Backend to use - "auto", "matugen", or "pillow"

    Returns:
        Tuple of (Theme, backend_used) where backend_used is the
        actual backend that was used ("matugen" or "pillow")

    Raises:
        ValueError: If neither image_path nor color provided
        RuntimeError: If requested backend is not available

    Examples:
        # From wallpaper with auto backend
        theme, used = generate_theme(image_path="~/wallpaper.jpg")

        # With specific scheme (requires matugen)
        theme, used = generate_theme(
            image_path="~/wallpaper.jpg",
            scheme="scheme-vibrant"
        )

        # From hex color
        theme, used = generate_theme(color="#e94560")

        # Force pillow backend
        theme, used = generate_theme(
            image_path="~/wallpaper.jpg",
            backend="pillow"
        )
    """
    # Validate input
    if not image_path and not color:
        raise ValueError("Must provide either image_path or color")

    # Normalize scheme name
    scheme = normalize_scheme_name(scheme)

    # Resolve backend
    actual_backend: str
    if backend == "auto":
        actual_backend = get_available_backend()
    else:
        actual_backend = backend

    # Validate backend availability
    if actual_backend == "matugen" and not is_matugen_available():
        raise RuntimeError(
            "matugen backend requested but not installed. "
            "Install with: paru -S matugen-bin or cargo install matugen"
        )

    # Generate theme using selected backend
    if actual_backend == "matugen":
        theme = generate_theme_from_matugen(
            image_path=image_path,
            color=color,
            scheme=scheme,
            dark_mode=dark_mode,
        )
    else:
        # Pillow backend
        theme = _generate_pillow_theme(
            image_path=image_path,
            color=color,
            scheme=scheme,
            dark_mode=dark_mode,
        )

    # Update global theme so get_current_theme() returns this theme
    set_current_theme(theme)

    return theme, actual_backend


def _generate_pillow_theme(
    image_path: str | None,
    color: str | None,
    scheme: str,
    dark_mode: bool,
) -> Theme:
    """Generate theme using pillow backend.

    Args:
        image_path: Path to wallpaper image
        color: Hex color string
        scheme: Scheme name (ignored, will warn if non-default)
        dark_mode: Whether to generate dark mode theme

    Returns:
        Theme instance
    """
    # Warn if non-default scheme requested
    if scheme != "scheme-tonal-spot":
        warnings.warn(
            f"Pillow backend ignores scheme parameter (got '{scheme}'). "
            "Install matugen for scheme support: paru -S matugen-bin",
            UserWarning,
            stacklevel=3,
        )

    if image_path:
        palette = palette_from_image(image_path, dark_mode=dark_mode)
    elif color:
        palette = generate_material_palette(color, dark_mode=dark_mode)
    else:
        raise ValueError("Either image_path or color must be provided")
    
    return Theme.from_material_palette(palette)


def list_schemes(include_display_names: bool = False) -> list[str] | dict[str, str]:
    """List available color schemes.

    Args:
        include_display_names: If True, return dict with display names

    Returns:
        List of scheme names, or dict mapping names to display names
    """
    if include_display_names:
        return SCHEME_DISPLAY_NAMES.copy()
    return MATUGEN_SCHEMES.copy()


# Re-export for convenience
__all__ = [
    "generate_theme",
    "get_available_backend",
    "get_backend_info",
    "list_schemes",
    "is_matugen_available",
    "Backend",
    "MATUGEN_SCHEMES",
    "SCHEME_DISPLAY_NAMES",
]
