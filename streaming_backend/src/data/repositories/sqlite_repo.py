import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# No direct config imports needed here


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration_seconds INTEGER,
            filename TEXT NOT NULL,
            thumbnail TEXT,
            tags TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            position_seconds INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, video_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()


def _seed_videos(conn: sqlite3.Connection) -> None:
    # Idempotent simple seed: if no videos, insert sample rows.
    # Filenames are relative to MEDIA_DIR (see src.core.config.MEDIA_DIR).
    cur = conn.execute("SELECT COUNT(*) as cnt FROM videos")
    cnt = cur.fetchone()["cnt"]
    if cnt == 0:
        now = datetime.now(timezone.utc).isoformat()
        samples = [
            {
                "title": "Sample Video 1",
                "description": "A sample video for demo.",
                "duration_seconds": 300,
                "filename": "sample1.mp4",
                "thumbnail": None,
                "tags": ["demo", "sample"],
                "created_at": now,
            },
            {
                "title": "Sample Video 2",
                "description": "Another sample video.",
                "duration_seconds": 620,
                "filename": "sample2.mp4",
                "thumbnail": None,
                "tags": ["demo"],
                "created_at": now,
            },
        ]
        for v in samples:
            conn.execute(
                """
                INSERT INTO videos (title, description, duration_seconds, filename, thumbnail, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    v["title"],
                    v["description"],
                    v["duration_seconds"],
                    v["filename"],
                    v["thumbnail"],
                    json.dumps(v["tags"]) if v["tags"] else None,
                    v["created_at"],
                ),
            )
        conn.commit()


class SQLiteConnectionManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def __call__(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = _dict_factory
        _ensure_schema(conn)
        _seed_videos(conn)
        return conn


class SQLiteUserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_user(self, email: str, password_hash: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?) RETURNING id, email, created_at",
            (email, password_hash, now),
        )
        row = cur.fetchone()
        self.conn.commit()
        return row

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cur.fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()


class SQLiteVideoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def list_videos(self) -> List[Dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM videos ORDER BY created_at DESC")
        rows = cur.fetchall()
        # Normalize tags
        for r in rows:
            if r.get("tags"):
                try:
                    r["tags"] = json.loads(r["tags"])
                except Exception:
                    r["tags"] = []
        return rows

    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        row = cur.fetchone()
        if row and row.get("tags"):
            try:
                row["tags"] = json.loads(row["tags"])
            except Exception:
                row["tags"] = []
        return row


class SQLiteHistoryRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_history(self, user_id: int, video_id: int, position_seconds: int) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        # Try update first
        cur = self.conn.execute(
            "UPDATE history SET position_seconds = ?, updated_at = ? WHERE user_id = ? AND video_id = ?",
            (position_seconds, now, user_id, video_id),
        )
        if cur.rowcount == 0:
            # Insert new
            self.conn.execute(
                "INSERT INTO history (user_id, video_id, position_seconds, updated_at) VALUES (?, ?, ?, ?)",
                (user_id, video_id, position_seconds, now),
            )
        self.conn.commit()
        cur2 = self.conn.execute(
            "SELECT * FROM history WHERE user_id = ? AND video_id = ?", (user_id, video_id)
        )
        return cur2.fetchone()

    def list_history_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT * FROM history WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)
        )
        return cur.fetchall()
