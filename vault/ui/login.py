from __future__ import annotations

import base64
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config import ConfigManager
from ..security import build_fernet, generate_salt, hash_password, verify_password


class LoginWindow(QWidget):
    authenticated = pyqtSignal(object)

    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        super().__init__()
        self.config = config or ConfigManager()
        self.setWindowTitle("Kakha's Password Vault - Access")
        self.setObjectName("LoginWindow")
        self.setMinimumSize(440, 420)
        self.stack = QStackedWidget()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.addWidget(self.stack)

        self.setup_widget = SetupWidget(self.config)
        self.login_widget = MasterLoginWidget(self.config)

        self.setup_widget.setup_complete.connect(self._handle_setup_complete)
        self.login_widget.authenticated.connect(self.authenticated)

        self.stack.addWidget(self.setup_widget)
        self.stack.addWidget(self.login_widget)

        if self.config.exists():
            self.stack.setCurrentWidget(self.login_widget)
        else:
            self.stack.setCurrentWidget(self.setup_widget)

        self.setStyleSheet(_LOGIN_STYLES)

    def _handle_setup_complete(self) -> None:
        self.stack.setCurrentWidget(self.login_widget)


class SetupWidget(QWidget):
    setup_complete = pyqtSignal()

    def __init__(self, config: ConfigManager) -> None:
        super().__init__()
        self.config = config
        self.setObjectName("SetupWidget")
        title = QLabel("Welcome to Kakha's Password Vault")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        subtitle = QLabel("Create your master password to begin securing your secrets.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Create master password")

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Confirm master password")

        self.error_label = QLabel()
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("Establish Vault")
        self.button.clicked.connect(self._save_master_password)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(16)
        layout.addWidget(self.password)
        layout.addWidget(self.confirm_password)
        layout.addWidget(self.button)
        layout.addWidget(self.error_label)
        layout.addStretch()

    def _save_master_password(self) -> None:
        password = self.password.text().strip()
        confirm = self.confirm_password.text().strip()

        if len(password) < 8:
            self.error_label.setText("Master password must be at least 8 characters long.")
            return
        if password != confirm:
            self.error_label.setText("Passwords do not match. Try again.")
            return

        salt = generate_salt()
        password_hash = hash_password(password, salt)
        config_payload = {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "password_hash": base64.b64encode(password_hash).decode("utf-8"),
        }
        self.config.write(config_payload)
        self.password.clear()
        self.confirm_password.clear()
        self.error_label.setText("")
        self.setup_complete.emit()


class MasterLoginWidget(QWidget):
    authenticated = pyqtSignal(object)

    def __init__(self, config: ConfigManager) -> None:
        super().__init__()
        self.config = config
        self.setObjectName("MasterLoginWidget")

        title = QLabel("Unlock Vault")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        subtitle = QLabel("Enter your master password to access your encrypted credentials.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Master password")

        self.error_label = QLabel()
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button = QPushButton("Unlock")
        self.button.clicked.connect(self._authenticate)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(16)
        layout.addWidget(self.password)
        layout.addWidget(self.button)
        layout.addWidget(self.error_label)
        layout.addStretch()

    def _authenticate(self) -> None:
        try:
            data = self.config.read()
        except FileNotFoundError:
            self.error_label.setText("Configuration missing. Please restart setup.")
            return

        password = self.password.text()
        salt = base64.b64decode(data["salt"])
        expected_hash = base64.b64decode(data["password_hash"])

        if not verify_password(password, salt, expected_hash):
            self.error_label.setText("Incorrect master password.")
            self.password.selectAll()
            return

        fernet = build_fernet(password, salt)
        self.password.clear()
        self.error_label.setText("")
        self.authenticated.emit(fernet)


_LOGIN_STYLES = """
#LoginWindow {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f2027,
        stop:0.5 #203a43,
        stop:1 #2c5364
    );
    color: #f0f3f5;
}

QLabel {
    font-family: "Segoe UI";
    color: #f0f3f5;
}

QLineEdit {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    background: rgba(10, 25, 47, 0.6);
    color: #e3f2fd;
}

QPushButton {
    background-color: #21c1d6;
    padding: 12px;
    border-radius: 8px;
    color: #08142b;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #26d6ed;
}

QPushButton:pressed {
    background-color: #18a0b3;
}

#ErrorLabel {
    color: #ff9f9f;
    min-height: 22px;
}
"""
