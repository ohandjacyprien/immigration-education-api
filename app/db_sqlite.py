import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

DB_PATH = Path(__file__).resolve().parent.parent / "data.sqlite3"

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 0,
        email_verified INTEGER NOT NULL DEFAULT 0,
        verify_token TEXT,
        verify_token_expires_at TEXT
    );""",
    """CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        provider TEXT,
        provider_ref TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );""",
    """CREATE TABLE IF NOT EXISTS premium_downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );""",
    """CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    );""",
]

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_columns() -> None:
    # Lightweight migration for older DBs
    cols_needed = {
        "is_active": "INTEGER NOT NULL DEFAULT 0",
        "email_verified": "INTEGER NOT NULL DEFAULT 0",
        "verify_token": "TEXT",
        "verify_token_expires_at": "TEXT",
    }
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(users)")
        existing = {r["name"] for r in cur.fetchall()}
        for name, ddl in cols_needed.items():
            if name not in existing:
                cur.execute(f"ALTER TABLE users ADD COLUMN {name} {ddl}")
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    conn = _conn()
    try:
        cur = conn.cursor()
        for stmt in SCHEMA:
            cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()
    _ensure_columns()

def fetch_one(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def fetch_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def execute(query: str, params: Tuple = ()) -> int:
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
