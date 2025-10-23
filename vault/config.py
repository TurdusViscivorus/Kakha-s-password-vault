from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

APP_NAME = "KakhasPasswordVault"


def _default_app_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / f".{APP_NAME}"


APP_DIR = _default_app_dir()
CONFIG_PATH = APP_DIR / "config.json"
DB_PATH = APP_DIR / "vault.db"


class ConfigManager:
    """Reads and writes application configuration."""

    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.path.exists()

    def read(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError("Configuration file does not exist.")
        with self.path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def write(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)
