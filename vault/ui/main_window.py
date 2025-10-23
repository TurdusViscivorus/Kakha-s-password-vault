from __future__ import annotations

from datetime import datetime
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QAction, QClipboard
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..database import VaultDatabase, VaultEntry
from ..security import decrypt, encrypt


class EntryDialog(QDialog):
    def __init__(self, parent=None, *, title="Add Entry", entry: Optional[VaultEntry] = None, password: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(420, 360)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit(entry.title if entry else "")
        self.username_edit = QLineEdit(entry.username if entry else "")
        self.password_edit = QLineEdit(password)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.url_edit = QLineEdit(entry.url if entry else "")
        self.notes_edit = QTextEdit(entry.notes if entry else "")

        form.addRow("Title", self.title_edit)
        form.addRow("Username", self.username_edit)
        form.addRow("Password", self.password_edit)
        form.addRow("URL", self.url_edit)
        form.addRow("Notes", self.notes_edit)

        layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save")
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._validate)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)

    def _validate(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Title is required.")
            return
        if not self.username_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Username is required.")
            return
        if not self.password_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Password is required.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "username": self.username_edit.text().strip(),
            "password": self.password_edit.text(),
            "url": self.url_edit.text().strip() or None,
            "notes": self.notes_edit.toPlainText().strip() or None,
        }


class MainWindow(QMainWindow):
    def __init__(self, database: VaultDatabase, fernet) -> None:
        super().__init__()
        self.database = database
        self.fernet = fernet
        self._entries_cache: dict[int, VaultEntry] = {}
        self.setWindowTitle("Kakha's Password Vault")
        self.setObjectName("MainWindow")
        self.resize(960, 640)

        self._setup_toolbar()
        self._setup_table()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Vault ready.")
        self._refresh_table()
        self._apply_styles()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        toolbar.setIconSize(QSize(28, 28))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        add_action = QAction("Add", self)
        add_action.triggered.connect(self._add_entry)
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self._edit_entry)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self._delete_entry)
        copy_action = QAction("Copy Password", self)
        copy_action.triggered.connect(self._copy_password)
        reveal_action = QAction("Reveal Password", self)
        reveal_action.triggered.connect(self._reveal_password)

        for action in (add_action, edit_action, delete_action, copy_action, reveal_action):
            toolbar.addAction(action)

    def _setup_table(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("Your encrypted credentials")
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Title", "Username", "URL", "Updated"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)

        layout.addWidget(header)
        layout.addWidget(self.table)

        self.setCentralWidget(central)

    def _apply_styles(self) -> None:
        self.setStyleSheet(_MAIN_STYLES)

    def _refresh_table(self) -> None:
        self.table.setSortingEnabled(False)
        entries = self.database.list_entries()
        self._entries_cache = {entry.id: entry for entry in entries}
        self.table.setRowCount(len(entries))
        for row_index, entry in enumerate(entries):
            title_item = QTableWidgetItem(entry.title)
            title_item.setData(Qt.ItemDataRole.UserRole, entry.id)
            self.table.setItem(row_index, 0, title_item)
            self.table.setItem(row_index, 1, QTableWidgetItem(entry.username))
            self.table.setItem(row_index, 2, QTableWidgetItem(entry.url or "-"))
            timestamp = datetime.fromisoformat(entry.updated_at)
            pretty = timestamp.strftime("%b %d, %Y %H:%M")
            self.table.setItem(row_index, 3, QTableWidgetItem(pretty))
            self.table.setRowHeight(row_index, 46)
        self.table.setSortingEnabled(True)
        self.table.sortItems(0)

    def _get_selected_entry(self) -> Optional[VaultEntry]:
        selected = self.table.currentRow()
        if selected < 0:
            return None
        item = self.table.item(selected, 0)
        if item is None:
            return None
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if entry_id is None:
            return None
        return self._entries_cache.get(entry_id)

    def _add_entry(self) -> None:
        dialog = EntryDialog(self, title="Add Credential")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            encrypted_password = encrypt(self.fernet, data["password"])
            self.database.add_entry(
                data["title"], data["username"], encrypted_password, data["url"], data["notes"]
            )
            self._refresh_table()
            self.status_bar.showMessage("Credential saved.", 4000)

    def _edit_entry(self) -> None:
        entry = self._get_selected_entry()
        if entry is None:
            QMessageBox.information(self, "Edit Entry", "Select an entry to edit.")
            return
        password = decrypt(self.fernet, entry.password_encrypted)
        dialog = EntryDialog(self, title="Edit Credential", entry=entry, password=password)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            encrypted_password = encrypt(self.fernet, data["password"])
            self.database.update_entry(
                entry.id,
                data["title"],
                data["username"],
                encrypted_password,
                data["url"],
                data["notes"],
            )
            self._refresh_table()
            self.status_bar.showMessage("Credential updated.", 4000)

    def _delete_entry(self) -> None:
        entry = self._get_selected_entry()
        if entry is None:
            QMessageBox.information(self, "Delete Entry", "Select an entry to delete.")
            return
        confirm = QMessageBox.question(
            self,
            "Delete Credential",
            f"Are you sure you want to delete '{entry.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.database.delete_entry(entry.id)
            self._refresh_table()
            self.status_bar.showMessage("Credential removed.", 4000)

    def _copy_password(self) -> None:
        entry = self._get_selected_entry()
        if entry is None:
            QMessageBox.information(self, "Copy Password", "Select an entry to copy.")
            return
        password = decrypt(self.fernet, entry.password_encrypted)
        QApplication.clipboard().setText(password, mode=QClipboard.Mode.Clipboard)
        self.status_bar.showMessage("Password copied to clipboard for 30 seconds.", 4000)
        QTimer.singleShot(30000, self._clear_clipboard)

    def _clear_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=QClipboard.Mode.Clipboard)

    def _reveal_password(self) -> None:
        entry = self._get_selected_entry()
        if entry is None:
            QMessageBox.information(self, "Reveal Password", "Select an entry to reveal.")
            return
        password = decrypt(self.fernet, entry.password_encrypted)
        QMessageBox.information(self, "Password", f"<b>{entry.title}</b><br><br>{password}")


_MAIN_STYLES = """
#MainWindow {
    background-color: #0b1729;
    color: #e3f2fd;
}

QToolBar {
    background: rgba(14, 30, 47, 0.8);
    border: none;
    padding: 12px;
    spacing: 18px;
}

QToolButton {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 10px 18px;
    color: #e3f2fd;
    font-weight: 600;
}

QToolButton:hover {
    background: rgba(255, 255, 255, 0.18);
}

#HeaderLabel {
    font-size: 24px;
    font-weight: 700;
}

QTableWidget {
    background: rgba(16, 40, 62, 0.8);
    border-radius: 12px;
    gridline-color: rgba(255, 255, 255, 0.05);
    color: #cfd8dc;
    selection-background-color: rgba(33, 193, 214, 0.5);
    selection-color: #10283e;
    font-size: 14px;
}

QHeaderView::section {
    background: rgba(33, 193, 214, 0.3);
    padding: 12px;
    border: none;
    color: #0b1729;
    font-weight: bold;
}

QScrollBar:vertical {
    width: 12px;
    background: rgba(8, 19, 33, 0.7);
}

QScrollBar::handle:vertical {
    background: rgba(33, 193, 214, 0.5);
    border-radius: 6px;
}

QMessageBox {
    background-color: #0b1729;
    color: #e3f2fd;
}
"""
