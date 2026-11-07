"""Spin box text clears the left border (Qt ignores the stylesheet padding)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QLineEdit, QSpinBox, QWidget

from glaze.theme import get_current_theme
from glaze.widgets import FramelessMainWindow, frameless_window, inset_spinbox_text


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _inset(box):
    return box.findChild(QLineEdit).textMargins().left()


def test_insets_every_spin_box_inside(app):
    root = QWidget()
    boxes = [QSpinBox(root), QDoubleSpinBox(root)]
    inset_spinbox_text(root)
    assert [_inset(b) for b in boxes] == [get_current_theme().padding_h] * 2


def test_insets_a_spin_box_passed_directly(app):
    box = QSpinBox()
    inset_spinbox_text(box)
    assert _inset(box) == get_current_theme().padding_h


def test_window_insets_spin_boxes_added_after_init(app, monkeypatch):
    # The real one runs `hyprctl dispatch setfloating active`
    monkeypatch.setattr(frameless_window, "hyprctl_float_active", lambda: None)

    class Window(FramelessMainWindow):
        def __init__(self):
            super().__init__(300, 200, "Test")
            self.spin = QSpinBox()
            self.content_layout.addWidget(self.spin)

    window = Window()
    assert _inset(window.spin) == 0
    window.show()
    assert _inset(window.spin) == get_current_theme().padding_h
    window.close()
