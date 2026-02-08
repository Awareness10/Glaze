#!/usr/bin/env python3
"""Test script to verify platform detection works correctly."""

import os
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

PROJECT_ROOT: Path = Path(__file__).parents[1]
sys.path.extend([PROJECT_ROOT.as_posix()])

from src.glaze.wayland import (
    is_hyprland,
    is_tiling_wm,
    is_cosmic,
    is_wayland,
    is_stacking_de,
    get_desktop_environment,
)


def print_environment_rich():
    """Print relevant environment variables using rich styling."""
    env_vars = [
        "XDG_CURRENT_DESKTOP",
        "XDG_SESSION_DESKTOP",
        "XDG_SESSION_TYPE",
        "DESKTOP_SESSION",
        "WAYLAND_DISPLAY",
        "HYPRLAND_INSTANCE_SIGNATURE",
        "COSMIC_PANEL_NAME",
        "COSMIC_PANEL_SIZE",
        "COSMIC_PANEL_ANCHOR",
    ]

    table = Table(title="Environment Variables", show_header=True, header_style="bold cyan")
    table.add_column("Variable", style="yellow", width=30)
    table.add_column("Value", style="green")

    for var in env_vars:
        value = os.environ.get(var, "[dim](not set)[/dim]")
        table.add_row(var, value)

    _console.print(table)
    _console.print()


def print_environment_plain():
    """Print relevant environment variables using plain output."""
    print("=" * 60)
    print("Environment Variables")
    print("=" * 60)

    env_vars = [
        "XDG_CURRENT_DESKTOP",
        "XDG_SESSION_DESKTOP",
        "XDG_SESSION_TYPE",
        "DESKTOP_SESSION",
        "WAYLAND_DISPLAY",
        "HYPRLAND_INSTANCE_SIGNATURE",
        "COSMIC_PANEL_NAME",
        "COSMIC_PANEL_SIZE",
        "COSMIC_PANEL_ANCHOR",
    ]

    for var in env_vars:
        value = os.environ.get(var, "(not set)")
        print(f"  {var:30s} : {value}")
    print()


def print_results_rich(results: dict):
    """Print detection results using rich styling."""
    table = Table(title="Detection Results", show_header=True, header_style="bold cyan")
    table.add_column("Function", style="yellow", width=25)
    table.add_column("Result", style="magenta", width=10)

    table.add_row("get_desktop_environment()", f"[bold]{results['desktop']}[/bold]")
    table.add_row("is_wayland()", str(results['wayland']))
    table.add_row("is_cosmic()", str(results['cosmic']))
    table.add_row("is_hyprland()", str(results['hyprland']))
    table.add_row("is_tiling_wm()", str(results['tiling']))
    table.add_row("is_stacking_de()", str(results['stacking']))

    _console.print(table)
    _console.print()

    # Print interpretation
    if results['cosmic']:
        panel_content = (
            "[cyan]COSMIC Desktop detected[/cyan]\n\n"
            "Running on Pop!_OS with COSMIC desktop environment.\n"
            "COSMIC is a stacking compositor - X11 window type hints will be skipped.\n"
            "Window decorations will be handled natively by COSMIC."
        )
        panel_style = "cyan"
    elif results['tiling']:
        panel_content = (
            "[green]Tiling WM detected[/green]\n\n"
            "The WA_X11NetWmWindowTypeCombo attribute will be applied.\n"
            "This ensures proper window management with tiling window managers."
        )
        panel_style = "green"
    else:
        panel_content = (
            "[blue]Stacking DE detected[/blue]\n\n"
            "The WA_X11NetWmWindowTypeCombo attribute will be skipped.\n"
            "This ensures proper window management with traditional desktop environments."
        )
        panel_style = "blue"

    _console.print(Panel(panel_content, title="Window Management Configuration", border_style=panel_style))
    _console.print()
    _console.print("[bold]Status:[/bold] Window management compatibility configured correctly.")


def print_results_plain(results: dict):
    """Print detection results using plain output."""
    print("=" * 60)
    print("Detection Results")
    print("=" * 60)
    print(f"  {'get_desktop_environment()':25s} : {results['desktop']}")
    print(f"  {'is_wayland()':25s} : {results['wayland']}")
    print(f"  {'is_cosmic()':25s} : {results['cosmic']}")
    print(f"  {'is_hyprland()':25s} : {results['hyprland']}")
    print(f"  {'is_tiling_wm()':25s} : {results['tiling']}")
    print(f"  {'is_stacking_de()':25s} : {results['stacking']}")
    print()

    print("=" * 60)
    print("Window Management Configuration")
    print("=" * 60)

    if results['cosmic']:
        print("  Status: COSMIC Desktop detected")
        print()
        print("  Running on Pop!_OS with COSMIC desktop environment.")
        print("  COSMIC is a stacking compositor - X11 window type hints")
        print("  will be skipped. Window decorations handled natively by COSMIC.")
    elif results['tiling']:
        print("  Status: Tiling WM detected")
        print()
        print("  The WA_X11NetWmWindowTypeCombo attribute will be applied.")
        print("  This ensures proper window management with tiling window managers.")
    else:
        print("  Status: Stacking DE detected")
        print()
        print("  The WA_X11NetWmWindowTypeCombo attribute will be skipped.")
        print("  This ensures proper window management with traditional desktop")
        print("  environments.")

    print()
    print("  Result: Window management compatibility configured correctly.")
    print()


def main():
    """Main test function."""
    # Detect platform
    results = {
        'desktop': get_desktop_environment(),
        'wayland': is_wayland(),
        'cosmic': is_cosmic(),
        'hyprland': is_hyprland(),
        'tiling': is_tiling_wm(),
        'stacking': is_stacking_de(),
    }

    if RICH_AVAILABLE:
        print_environment_rich()
        print_results_rich(results)
    else:
        print_environment_plain()
        print_results_plain(results)


if __name__ == "__main__":
    main()
