import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Iterable, Tuple, List


def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                session_id TEXT NOT NULL,
                event TEXT NOT NULL,
                payload TEXT
            )
            """
        )
        conn.commit()


def log_event(db_path: Path, session_id: str, event: str, payload: dict | None = None, enabled: bool = True) -> None:
    if not enabled:
        return
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO logs (ts, session_id, event, payload) VALUES (?, ?, ?, ?)",
            (
                datetime.utcnow().isoformat(timespec="seconds") + "Z",
                session_id,
                event,
                json.dumps(payload or {}, ensure_ascii=False),
            ),
        )
        conn.commit()


def export_logs(db_path: Path, session_id: str) -> bytes:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT ts, event, payload FROM logs WHERE session_id=? ORDER BY id ASC",
            (session_id,),
        )
        rows = cur.fetchall()
    # Return JSONL as bytes
    lines: List[str] = []
    for ts, event, payload in rows:
        rec = {"ts": ts, "session_id": session_id, "event": event, "payload": json.loads(payload or "{}")}
        lines.append(json.dumps(rec, ensure_ascii=False))
    return ("\n".join(lines)).encode("utf-8")


def fetch_recent_logs(db_path: Path, session_id: str, limit: int = 50) -> Iterable[Tuple[str, str, str]]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT ts, event, payload FROM logs WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        )
        yield from cur.fetchall()