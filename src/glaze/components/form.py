import sys
from PySide6.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from glaze.widgets import ThemedComboBox, FramelessMainWindow


class LoginWindow(FramelessMainWindow):
    """Login form with custom frameless titlebar."""

    def __init__(self):
        super().__init__(width=380, height=480, title="Login")

    def setup_content(self):
        """Set up the login form UI."""
        self.content_layout.setContentsMargins(40, 30, 40, 40)
        self.content_layout.setSpacing(16)

        # Title
        title = QLabel("Welcome Back")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title)

        subtitle = QLabel("Sign in to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")
        self.content_layout.addWidget(subtitle)
        self.content_layout.addSpacing(20)

        # Email field
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email address")
        self.email.setMinimumHeight(45)
        self.content_layout.addWidget(self.email)

        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(45)
        self.content_layout.addWidget(self.password)

        # Role selector
        self.role = ThemedComboBox()
        self.role.addItems(["User", "Admin", "Guest"])
        self.role.setMinimumHeight(45)
        self.content_layout.addWidget(self.role)

        self.content_layout.addSpacing(10)

        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        self.content_layout.addWidget(login_btn)

        self.content_layout.addStretch()

    def handle_login(self):
        email, pwd = self.email.text(), self.password.text()
        if email and pwd:
            QMessageBox.information(self, "Success", f"Welcome, {email}!")
        else:
            QMessageBox.warning(self, "Error", "Please fill all fields")


def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
