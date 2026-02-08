import sys
import csv
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QComboBox, QMessageBox, QFileDialog, QFrame,
    QGraphicsDropShadowEffect, QGridLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from glaze.theme import get_dialog_stylesheet, get_table_container_style
from glaze.widgets import ThemedComboBox, RoundedHeaderView, FramelessMainWindow

DATA_FILE = "users.csv"


class UserDialog(QDialog):
    """Dialog for adding/editing users."""

    def __init__(self, parent: QWidget | None = None, user_data: tuple[str, str, str, str] | None = None):
        super().__init__(parent)
        self.user_id = user_data[0] if user_data else None
        self.setWindowTitle("Edit User" if user_data else "Add User")
        self.setFixedSize(420, 280)
        self.setup_ui(user_data)
        self.setStyleSheet(get_dialog_stylesheet())

    def setup_ui(self, user_data: tuple[str, str, str, str] | None) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        form = QGridLayout()
        form.setColumnMinimumWidth(0, 60)
        form.setColumnStretch(1, 1)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(16)

        labels = ["Name:", "Email:", "Status:"]
        for i, text in enumerate(labels):
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("font-size: 14px;")
            label.setFixedHeight(44)
            form.addWidget(label, i, 0)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.name_input.setFixedHeight(44)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.setFixedHeight(44)

        self.status_input = ThemedComboBox()
        self.status_input.addItems(["Active", "Inactive", "Pending"])
        self.status_input.setFixedHeight(44)

        form.addWidget(self.name_input, 0, 1)
        form.addWidget(self.email_input, 1, 1)
        form.addWidget(self.status_input, 2, 1)

        if user_data:
            self.name_input.setText(user_data[1])
            self.email_input.setText(user_data[2])
            self.status_input.setCurrentText(user_data[3])

        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setFixedWidth(100)
        save_btn.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def validate_and_accept(self) -> None:
        if not all([self.name_input.text(), self.email_input.text()]):
            QMessageBox.warning(self, "Validation Error", "Name and email are required.")
            return
        self.accept()

    def get_data(self) -> tuple[str, str, str]:
        return (
            self.name_input.text(),
            self.email_input.text(),
            self.status_input.currentText()
        )


class DataTableWindow(FramelessMainWindow):
    """Data table window with custom frameless titlebar."""

    def __init__(self):
        super().__init__(width=750, height=550, title="User Management")
        self.load_data()

    def setup_content(self) -> None:
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search users...")
        self.search.setFixedHeight(42)
        self.search.textChanged.connect(self.filter_table)
        toolbar.addWidget(self.search)

        self.add_btn = QPushButton("+ Add User")
        self.add_btn.setFixedHeight(42)
        self.add_btn.clicked.connect(self.add_user)
        toolbar.addWidget(self.add_btn)
        self.content_layout.addLayout(toolbar)

        # Table container with shadow
        table_container = QFrame()
        table_container.setObjectName("tableContainer")
        table_container.setStyleSheet(get_table_container_style())
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        table_container.setGraphicsEffect(shadow)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Status"])
        self.table.doubleClicked.connect(self.edit_selected_user)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.Shape.NoFrame)

        header = RoundedHeaderView(Qt.Orientation.Horizontal, self.table)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setHorizontalHeader(header)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        if (v_header := self.table.verticalHeader()) is not None:
            v_header.setVisible(False)

        table_layout.addWidget(self.table)
        self.content_layout.addWidget(table_container)

        footer = QHBoxLayout()
        footer.addStretch()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedSize(100, 40)
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.delete_selected)
        footer.addWidget(self.delete_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setFixedSize(100, 40)
        self.edit_btn.setObjectName("secondary")
        self.edit_btn.clicked.connect(self.edit_selected_user)
        footer.addWidget(self.edit_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.setFixedSize(100, 40)
        self.export_btn.setObjectName("secondary")
        self.export_btn.clicked.connect(self.export_to_csv)
        footer.addWidget(self.export_btn)

        self.content_layout.addLayout(footer)

    def load_data(self) -> None:
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                data = [(row[0], row[1], row[2], row[3]) for row in reader if len(row) == 4]

            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                self._set_row_data(row, record)

        except OSError as e:
            QMessageBox.warning(self, "Load Failed", f"Could not load data: {e}")

    def _set_row_data(self, row: int, data: tuple[str, str, str, str]) -> None:
        for col, val in enumerate(data):
            item = QTableWidgetItem(val)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)

    def _get_row_data(self, row: int) -> tuple[str, str, str, str] | None:
        items = [self.table.item(row, col) for col in range(4)]
        if all(items):
            return tuple(item.text() for item in items)  # type: ignore[return-value]
        return None

    def _generate_next_id(self) -> str:
        max_id = 0
        for row in range(self.table.rowCount()):
            if item := self.table.item(row, 0):
                try:
                    max_id = max(max_id, int(item.text()))
                except ValueError:
                    pass
        return f"{max_id + 1:03d}"

    def _save_data(self) -> None:
        try:
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Email", "Status"])
                for row in range(self.table.rowCount()):
                    if row_data := self._get_row_data(row):
                        writer.writerow(row_data)
        except OSError:
            pass

    def add_user(self) -> None:
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, email, status = dialog.get_data()
            new_id = self._generate_next_id()
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._set_row_data(row, (new_id, name, email, status))
            self._save_data()

    def edit_selected_user(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a user to edit.")
            return

        row = selected[0].row()
        current_data = self._get_row_data(row)
        if current_data is None:
            return

        dialog = UserDialog(self, current_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, email, status = dialog.get_data()
            self._set_row_data(row, (current_data[0], name, email, status))
            self._save_data()

    def delete_selected(self) -> None:
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()), reverse=True)
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select user(s) to delete.")
            return

        count = len(selected_rows)
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {count} user{'s' if count > 1 else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                self.table.removeRow(row)
            self._save_data()

    def export_to_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "users.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                headers = [
                    item.text()
                    for col in range(self.table.columnCount())
                    if (item := self.table.horizontalHeaderItem(col)) is not None
                ]
                writer.writerow(headers)
                for row in range(self.table.rowCount()):
                    row_data = self._get_row_data(row)
                    if row_data:
                        writer.writerow(row_data)
            QMessageBox.information(self, "Export Complete", f"Exported to {path}")
        except OSError as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def filter_table(self, text: str) -> None:
        for row in range(self.table.rowCount()):
            match = any(
                (item := self.table.item(row, col)) is not None
                and text.lower() in item.text().lower()
                for col in range(self.table.columnCount())
            )
            self.table.setRowHidden(row, not match)


def main():
    app = QApplication(sys.argv)
    window = DataTableWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
