from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import DB_PATH


@dataclass
class VaultEntry:
    id: int
    title: str
    username: str
    password_encrypted: bytes
    url: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str


class VaultDatabase:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password_encrypted BLOB NOT NULL,
                    url TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def list_entries(self) -> List[VaultEntry]:
        cur = self.conn.execute(
            "SELECT id, title, username, password_encrypted, url, notes, created_at, updated_at FROM entries ORDER BY title COLLATE NOCASE"
        )
        rows = cur.fetchall()
        return [VaultEntry(**dict(row)) for row in rows]

    def add_entry(
        self,
        title: str,
        username: str,
        password_encrypted: bytes,
        url: Optional[str],
        notes: Optional[str],
    ) -> int:
        timestamp = datetime.utcnow().isoformat()
        with self.conn:
            cur = self.conn.execute(
                """
                INSERT INTO entries (title, username, password_encrypted, url, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, username, password_encrypted, url, notes, timestamp, timestamp),
            )
        return int(cur.lastrowid)

    def update_entry(
        self,
        entry_id: int,
        title: str,
        username: str,
        password_encrypted: bytes,
        url: Optional[str],
        notes: Optional[str],
    ) -> None:
        timestamp = datetime.utcnow().isoformat()
        with self.conn:
            self.conn.execute(
                """
                UPDATE entries
                SET title = ?, username = ?, password_encrypted = ?, url = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, username, password_encrypted, url, notes, timestamp, entry_id),
            )

    def delete_entry(self, entry_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))

    def close(self) -> None:
        self.conn.close()
