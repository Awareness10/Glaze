#!/usr/bin/env python3
"""Nuitka build script for glaze components.

This script compiles PySide6 applications into single-file executables using Nuitka.
Each component is built separately, producing optimized binaries with zstd compression in the dist/ directory.

Usage:
    python build.py                    # Build all components
    python build.py --component form   # Build specific component
    python build.py --debug            # Debug build (faster, with console)
    python build.py --clean            # Clean build artifacts
    python build.py --help             # Show help
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
    _console = Console()
except ImportError:
    RICH_AVAILABLE = False
    _console = None  # type: ignore


# Project paths
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# Component definitions: (module_path, output_name)
COMPONENTS = {
    "launcher": ("glaze.__main__", "glaze-launcher"),
    "form": ("glaze.components.form", "login-form"),
    "data_table": ("glaze.components.data_table", "data-table"),
    "settings": ("glaze.components.settings", "settings-dialog"),
}


def log_info(message: str):
    """Log informational message."""
    if RICH_AVAILABLE and _console:
        _console.print(f"[blue]INFO:[/blue] {message}")
    else:
        print(f"INFO: {message}")


def log_success(message: str):
    """Log success message."""
    if RICH_AVAILABLE and _console:
        _console.print(f"[green]SUCCESS:[/green] {message}")
    else:
        print(f"SUCCESS: {message}")


def log_warning(message: str):
    """Log warning message."""
    if RICH_AVAILABLE and _console:
        _console.print(f"[yellow]WARNING:[/yellow] {message}")
    else:
        print(f"WARNING: {message}")


def log_error(message: str):
    """Log error message."""
    if RICH_AVAILABLE and _console:
        _console.print(f"[red]ERROR:[/red] {message}")
    else:
        print(f"ERROR: {message}")


def clean_build_artifacts():
    """Remove build and dist directories."""
    log_info("Cleaning build artifacts...")
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            log_info(f"  Removed {directory}")
    log_success("Clean complete")
    print()


def build_component(module_path: str, output_name: str, debug: bool = False):
    """Build a single component using Nuitka.

    Args:
        module_path: Python module path (e.g., 'glaze.components.form')
        output_name: Output binary name (e.g., 'login-form')
        debug: If True, build in debug mode (faster, with console)
    """
    log_info(f"Building {output_name}...")

    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)

    # Convert module path to file path and determine if it's a __main__ module
    module_parts = module_path.split(".")
    is_main_module = module_parts[-1] == "__main__"

    if is_main_module:
        # For __main__ modules, use the package directory (not __main__.py itself)
        # This avoids the Nuitka warning about compiling __main__.py directly
        file_path = SRC_DIR.joinpath(*module_parts[:-1])
    else:
        # For regular modules, use the .py file
        file_path = SRC_DIR.joinpath(*module_parts[:-1]) / f"{module_parts[-1]}.py"

    if not file_path.exists():
        log_error(f"Could not find source file: {file_path}")
        return False

    # Base Nuitka command with optimizations
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",                       # Single compressed executable
        "--enable-plugin=pyside6",         # PySide6 plugin (handles Qt dependencies)
        "--follow-imports",                # Include all imported modules
        "--output-dir=build",              # Build cache directory
        f"--output-filename={output_name}",       # Binary name
        "--assume-yes-for-downloads",      # Auto-download dependencies
        "--jobs=4",                        # Parallel compilation (adjust based on CPU)
        "--include-data-dir=src/glaze/assets=glaze/assets",
    ]

    # Add --python-flag=-m for __main__ modules (recommended by Nuitka)
    # Don't include the package again to avoid warning
    if is_main_module:
        cmd.append("--python-flag=-m")
    else:
        # Only include package for non-main modules
        cmd.append("--include-package=glaze")

    # Performance optimizations (production builds)
    if not debug:
        cmd.extend([
            "--lto=yes",                       # Link-time optimization for smaller/faster binaries
            # Compression is enabled by default when zstandard is installed
            "--noinclude-qt-translations",     # Skip unused Qt translations
            "--prefer-source-code",            # Use source over bytecode for better optimization
            "--python-flag=no_site",           # Skip site-packages overhead
            "--python-flag=no_docstrings",     # Remove docstrings (smaller binary)
            "--python-flag=no_asserts",        # Remove assert statements
            "--remove-output",                 # Clean up intermediate build files
            "--quiet",                         # Reduce output noise
        ])
    # Debug mode options (faster compilation)
    else:
        cmd.extend([
            "--debug",                         # Include debug symbols
            "--show-progress",                 # Show compilation progress
        ])
        log_info("  Debug mode enabled (faster build, with console)")

    # Add the source file/directory to compile
    cmd.append(str(file_path))

    # Run Nuitka
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)

        # With --onefile, Nuitka creates: build/<output_filename>.bin (Linux)
        # The .bin extension is added automatically on Linux
        built_binary = BUILD_DIR / f"{output_name}.bin"
        if not built_binary.exists():
            # Fallback: try without .bin extension
            built_binary = BUILD_DIR / output_name

        if built_binary.exists():
            # Copy single executable to dist/
            dest_binary = DIST_DIR / output_name
            shutil.copy2(built_binary, dest_binary)
            # Make executable
            dest_binary.chmod(0o755)
            log_success(f"Built {output_name} -> dist/{output_name}")
        else:
            log_warning(f"Could not find built binary at {BUILD_DIR / output_name}")
            return False

    except subprocess.CalledProcessError as e:
        log_error(f"Build failed for {output_name}: {e}")
        return False

    return True


def build_all(debug: bool = False):
    """Build all components."""
    if RICH_AVAILABLE and _console:
        _console.print(Panel.fit(
            "[bold cyan]Building All Components[/bold cyan]",
            border_style="cyan"
        ))
    else:
        print("\n" + "="*60)
        print("Building all components...")
        print("="*60)
    print()

    success_count = 0
    failed = []

    for name, (module_path, output_name) in COMPONENTS.items():
        if build_component(module_path, output_name, debug):
            success_count += 1
        else:
            failed.append(output_name)
        print()

    # Build summary
    if RICH_AVAILABLE and _console:
        table = Table(title="Build Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Components", str(len(COMPONENTS)))
        table.add_row("Successful", str(success_count))
        table.add_row("Failed", str(len(failed)))
        table.add_row("Output Directory", str(DIST_DIR))

        _console.print(table)

        if failed:
            _console.print(f"\n[red]Failed components:[/red] {', '.join(failed)}")
    else:
        print("="*60)
        print(f"Build complete: {success_count}/{len(COMPONENTS)} components built successfully")
        print(f"Binaries located in: {DIST_DIR}")
        if failed:
            print(f"Failed: {', '.join(failed)}")
        print("="*60)


def main():
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(
        description="Build glaze components with Nuitka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                       # Build all components
  python build.py --component form      # Build only login form
  python build.py --component launcher  # Build only launcher
  python build.py --debug               # Debug build (faster)
  python build.py --clean               # Clean build artifacts

Available components:
  - launcher    : Interactive component selector
  - form        : Login form demo
  - data_table  : Data table with CRUD operations
  - settings    : Settings/preferences dialog
        """
    )

    parser.add_argument(
        "--component",
        choices=COMPONENTS.keys(),
        help="Build specific component only"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Build in debug mode (faster, with console)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts and exit"
    )

    args = parser.parse_args()

    # Clean mode
    if args.clean:
        clean_build_artifacts()
        return

    # Check if nuitka is installed
    try:
        subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("Nuitka not found. Install with: pip install nuitka")
        sys.exit(1)

    # Check if patchelf is installed (required for standalone builds on Linux)
    try:
        subprocess.run(
            ["patchelf", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("patchelf not found (required for standalone builds on Linux)")
        print("   Install with: sudo pacman -S patchelf  # CachyOS/Arch")
        print("   or: sudo apt install patchelf  # Debian/Ubuntu")
        print("   or: sudo dnf install patchelf  # Fedora")
        sys.exit(1)

    # Build specific component or all
    if args.component:
        module_path, output_name = COMPONENTS[args.component]
        if build_component(module_path, output_name, args.debug):
            log_success(f"Build complete: dist/{output_name}/{output_name}")
        else:
            sys.exit(1)
    else:
        build_all(args.debug)


if __name__ == "__main__":
    main()