"""get_matugen_colors only reads colors: matugen must run with --dry-run.

Without it, matugen applies every template in the user's matugen config and
sets the wallpaper, so building a theme would re-theme the whole desktop.
"""

import json
import subprocess

import pytest

from glaze import matugen

FAKE_OUTPUT = json.dumps({
    "colors": {
        "primary": {"dark": {"color": "#aabbcc"}, "light": {"color": "#112233"}},
        "surface": {"dark": "#000000", "light": "#ffffff"},  # pre-4.0 format
    }
})


@pytest.fixture
def commands(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout=FAKE_OUTPUT, stderr="")

    monkeypatch.setattr(matugen.subprocess, "run", fake_run)
    return calls


def test_image_mode_is_dry_run(commands, tmp_path):
    image = tmp_path / "wall.png"
    image.write_bytes(b"")
    matugen.get_matugen_colors(image_path=str(image))
    assert commands[0][:2] == ["matugen", "image"]
    assert "--dry-run" in commands[0]


def test_color_mode_is_dry_run(commands):
    matugen.get_matugen_colors(color="e94560")
    assert commands[0][:3] == ["matugen", "color", "hex"]
    assert "--dry-run" in commands[0]


def test_reads_both_json_formats(commands):
    colors = matugen.get_matugen_colors(color="#e94560")
    assert colors == {"primary": "#aabbcc", "surface": "#000000"}
