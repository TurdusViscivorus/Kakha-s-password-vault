from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

from .config import ConfigManager
from .database import VaultDatabase


class VaultApp(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("Kakha's Password Vault")
        self.setStyle("Fusion")
        self._apply_palette()
        self.config = ConfigManager()
        self.database: Optional[VaultDatabase] = None
        self.fernet = None
        self._load_stylesheet()

    def initialize_database(self) -> None:
        if self.database is None:
            self.database = VaultDatabase()

    def set_fernet(self, fernet) -> None:
        self.fernet = fernet

    def _apply_palette(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(11, 23, 41))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(227, 242, 253))
        palette.setColor(QPalette.ColorRole.Base, QColor(13, 32, 52))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(18, 45, 70))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(240, 243, 245))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(15, 32, 48))
        palette.setColor(QPalette.ColorRole.Text, QColor(227, 242, 253))
        palette.setColor(QPalette.ColorRole.Button, QColor(13, 32, 52))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(227, 242, 253))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(33, 193, 214))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(16, 40, 62))
        self.setPalette(palette)

    def _load_stylesheet(self) -> None:
        candidates = [Path(__file__).parent]
        if hasattr(sys, "_MEIPASS"):
            candidates.insert(0, Path(sys._MEIPASS) / "vault")
        for base_dir in candidates:
            style_path = base_dir / "ui" / "styles.qss"
            if style_path.exists():
                with style_path.open("r", encoding="utf-8") as fp:
                    self.setStyleSheet(self.styleSheet() + "\n" + fp.read())
                break


__all__ = ["VaultApp"]
