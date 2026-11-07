"""Indent spin box text to match the theme's padding.

Qt (6.12) ignores stylesheet padding for a spin box's text field, and
stylesheet rules for its inner QLineEdit too, so the text sits on the left
border. The inset is set on the line edit directly instead.
"""

from PySide6.QtWidgets import QAbstractSpinBox, QLineEdit, QWidget

from ..theme import get_current_theme


def inset_spinbox_text(root: QWidget) -> None:
    """Indent the text of root (if a spin box) and every spin box inside it.

    FramelessMainWindow calls this when shown and on refresh_theme(); call it
    for spin boxes added later.
    """
    inset = get_current_theme().padding_h
    boxes = root.findChildren(QAbstractSpinBox)
    if isinstance(root, QAbstractSpinBox):
        boxes.append(root)
    for box in boxes:
        edit = box.findChild(QLineEdit)
        if edit is not None:
            margins = edit.textMargins()
            edit.setTextMargins(inset, margins.top(), margins.right(), margins.bottom())
