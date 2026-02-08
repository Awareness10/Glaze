#!/usr/bin/env python3
"""Simple launcher for glaze components with Material You theme support.

This file provides a quick entry point to run the interactive component launcher.
Supports Material You theme generation from wallpaper images with multiple
color scheme variants via matugen or fallback to Pillow extraction.

Usage:
    python main.py                                 # Launch with default theme
    python main.py wallpaper.png                   # Generate theme from wallpaper
    python main.py wallpaper.png --scheme vibrant  # With specific scheme
    python main.py --color "#e94560"               # Generate theme from color
    python main.py --list-schemes                  # Show available schemes
    python main.py wallpaper.png --backend pillow  # Force Pillow backend
"""
import sys
import argparse
from pathlib import Path

from glaze.color_backend import Backend

# Add src directory to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


# Short scheme names (without "scheme-" prefix) for CLI convenience
SCHEME_CHOICES = [
    "tonal-spot", "vibrant", "expressive", "rainbow",
    "fruit-salad", "fidelity", "content", "monochrome", "neutral"
]


def list_schemes():
    """Print available color schemes and exit."""
    try:
        from glaze import MATUGEN_SCHEMES, SCHEME_DISPLAY_NAMES, is_matugen_available
    except ImportError as e:
        print(f"Error importing glaze: {e}")
        sys.exit(1)

    print("Available Color Schemes:")
    print("-" * 40)
    for scheme in MATUGEN_SCHEMES:
        display = SCHEME_DISPLAY_NAMES.get(scheme, scheme)
        # Short name for CLI
        short = scheme.replace("scheme-", "")
        print(f"  {short:<14} {display}")

    print()
    matugen_status = "installed" if is_matugen_available() else "not installed"
    print(f"Matugen status: {matugen_status}")
    if not is_matugen_available():
        print("Note: Scheme selection requires matugen. Install with:")
        print("  Arch: paru -S matugen-bin")
        print("  Cargo: cargo install matugen")


def apply_material_theme(
    image_path: str | None = None,
    color: str | None = None,
    scheme: str = "tonal-spot",
    backend: Backend = "auto",
    light_mode: bool = False
) -> bool:
    """Apply Material You theme from image or color.

    Args:
        image_path: Path to wallpaper image
        color: Hex color string
        scheme: Color scheme (short name without "scheme-" prefix)
        backend: Backend to use (auto, matugen, pillow)
        light_mode: Whether to use light mode

    Returns:
        True if successful, False otherwise
    """
    try:
        from glaze import generate_theme, SCHEME_DISPLAY_NAMES
        import glaze
    except ImportError as e:
        print(f"Error importing glaze: {e}")
        return False

    # Normalize scheme name
    full_scheme = f"scheme-{scheme}" if not scheme.startswith("scheme-") else scheme

    try:
        source = image_path or color
        source_type = "image" if image_path else "color"
        scheme_display = SCHEME_DISPLAY_NAMES.get(full_scheme, scheme)

        print("Generating Material You theme...")
        print(f"  Source: {source} ({source_type})")
        print(f"  Scheme: {scheme_display}")
        print(f"  Backend: {backend}")
        print(f"  Mode: {'light' if light_mode else 'dark'}")

        theme, used_backend = generate_theme(
            image_path=image_path,
            color=color,
            scheme=full_scheme,
            dark_mode=not light_mode,
            backend=backend,
        )

        # Update the theme in the theme module
        import sys as sys_module
        theme_module = sys_module.modules['glaze.theme']
        theme_module.theme = theme # type: ignore
        glaze.theme = theme

        print(f"\nTheme generated successfully using {used_backend} backend")
        print(f"  Accent: {theme.accent}")
        print(f"  Background: {theme.bg_primary}")
        return True

    except RuntimeError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Error generating theme: {e}")
        return False


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Glaze Launcher with Material You support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Default theme
  python main.py wallpaper.png                # Generate from wallpaper
  python main.py wallpaper.png --scheme vibrant  # Vibrant scheme
  python main.py --color "#e94560"            # Generate from color
  python main.py wallpaper.png --light        # Light mode theme
  python main.py wallpaper.png --backend pillow  # Force Pillow
  python main.py --list-schemes               # Show available schemes
        """
    )

    parser.add_argument(
        'wallpaper',
        nargs='?',
        help='Path to wallpaper image for Material You theme generation'
    )
    parser.add_argument(
        '--color',
        type=str,
        help='Hex color for Material You theme (e.g., "#e94560")'
    )
    parser.add_argument(
        '--scheme',
        type=str,
        default='tonal-spot',
        choices=SCHEME_CHOICES,
        help='Color scheme variant (default: tonal-spot). Requires matugen.'
    )
    parser.add_argument(
        '--backend',
        type=str,
        choices=['auto', 'matugen', 'pillow'],
        default='auto',
        help='Color extraction backend (default: auto)'
    )
    parser.add_argument(
        '--light',
        action='store_true',
        help='Generate light mode theme (default: dark mode)'
    )
    parser.add_argument(
        '--list-schemes',
        action='store_true',
        help='List available color schemes and exit'
    )

    args = parser.parse_args()

    # Handle --list-schemes
    if args.list_schemes:
        list_schemes()
        sys.exit(0)

    # Apply Material You theme if wallpaper or color provided
    if args.wallpaper or args.color:
        # Validate wallpaper path if provided
        if args.wallpaper:
            wallpaper_path = Path(args.wallpaper)
            if not wallpaper_path.exists():
                print(f"Error: Wallpaper file not found: {args.wallpaper}")
                sys.exit(1)

        # Generate and apply theme
        success = apply_material_theme(
            image_path=args.wallpaper,
            color=args.color,
            scheme=args.scheme,
            backend=args.backend,
            light_mode=args.light
        )

        if not success:
            print("Failed to apply Material You theme, using default theme")

    # Launch the interactive launcher
    from glaze.__main__ import main as launcher_main
    launcher_main()


if __name__ == "__main__":
    main()
