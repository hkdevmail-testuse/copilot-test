import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import get_db_path


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    avatar_key TEXT,
    thumbnail_key TEXT,
    avatar_url TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    diff TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db(db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = Path(db_path or get_db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_user(conn: sqlite3.Connection, user_id: str, email: str | None = None) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        default_email = email or f"{user_id}@example.com"
        conn.execute(
            "INSERT INTO users (id, email, first_name, last_name, phone, avatar_url, version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, default_email, "", "", None, None, 1),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row)


def get_profile(conn: sqlite3.Connection, user_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row is not None else None


def update_profile(
    conn: sqlite3.Connection,
    user_id: str,
    first_name: str,
    last_name: str,
    phone: str | None,
    avatar_key: str | None,
    thumbnail_key: str | None,
    avatar_url: str | None,
    provided_version: int | None,
    actor_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    existing = ensure_user(conn, user_id)
    current_version = int(existing["version"])

    if provided_version is not None and current_version != provided_version:
        raise ValueError("stale_version")

    updated_fields: dict[str, Any] = {}
    if first_name != existing["first_name"]:
        updated_fields["first_name"] = first_name
    if last_name != existing["last_name"]:
        updated_fields["last_name"] = last_name
    if phone != existing["phone"]:
        updated_fields["phone"] = phone
    if avatar_key != existing["avatar_key"]:
        updated_fields["avatar_key"] = avatar_key
    if thumbnail_key != existing["thumbnail_key"]:
        updated_fields["thumbnail_key"] = thumbnail_key
    if avatar_url != existing["avatar_url"]:
        updated_fields["avatar_url"] = avatar_url

    new_version = current_version + 1
    conn.execute(
        "UPDATE users SET first_name = ?, last_name = ?, phone = ?, avatar_key = ?, thumbnail_key = ?, avatar_url = ?, version = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (first_name, last_name, phone, avatar_key, thumbnail_key, avatar_url, new_version, user_id),
    )
    conn.commit()

    conn.execute(
        "INSERT INTO audits (object_type, object_id, actor_id, action, diff) VALUES (?, ?, ?, ?, ?)",
        ("profile", user_id, actor_id, "updated", json.dumps(updated_fields)),
    )
    conn.commit()

    profile = get_profile(conn, user_id)
    return profile or {}, updated_fields


def phone_exists(conn: sqlite3.Connection, phone: str, user_id: str | None = None) -> bool:
    if phone is None:
        return False
    if user_id is None:
        row = conn.execute("SELECT 1 FROM users WHERE phone = ?", (phone,)).fetchone()
    else:
        row = conn.execute("SELECT 1 FROM users WHERE phone = ? AND id != ?", (phone, user_id)).fetchone()
    return row is not None
