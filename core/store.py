"""SQLite persistence for tasks and append-only operational audit events."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL_STATES = {"SUCCEEDED", "BLOCKED", "HUMAN_REVIEW", "RESEARCH_ONLY", "NEEDS_ADAPTER"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class TaskStore:
    """Durable SQLite queue with atomic claims and an append-only audit trail."""
    def __init__(self, database: str = "data/multitareas.db") -> None:
        if database == ":memory:":
            raise ValueError("TaskStore requires a file-backed database for durable queue semantics")
        self.database = database
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 15000")
        return conn

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    pulpo TEXT NOT NULL,
                    vertical TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    available_at TEXT NOT NULL,
                    result TEXT,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_ready
                    ON tasks(state, available_at, created_at);
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(task_id)
                );
            """)

    def enqueue(self, task_id: str, pulpo: str, vertical: str,
                payload: dict[str, Any], idempotency_key: str | None = None,
                max_attempts: int = 3) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id is required")
        if not isinstance(pulpo, str) or not isinstance(vertical, str) or not vertical.strip():
            raise ValueError("pulpo and vertical are required")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        now = utc_now()
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        with self._connect() as db:
            if idempotency_key:
                row = db.execute("SELECT * FROM tasks WHERE idempotency_key = ?",
                                 (idempotency_key,)).fetchone()
                if row:
                    return dict(row)
            db.execute("""
                INSERT INTO tasks(task_id,idempotency_key,pulpo,vertical,payload,state,
                                  attempts,max_attempts,available_at,created_at,updated_at)
                VALUES(?,?,?,?,?,'QUEUED',0,?,?,?,?)
            """, (task_id, idempotency_key, pulpo, vertical, encoded,
                  max_attempts, now, now, now))
            self._audit(db, task_id, "TASK_QUEUED", "runtime",
                        {"pulpo": pulpo, "vertical": vertical})
            return dict(db.execute("SELECT * FROM tasks WHERE task_id = ?",
                                   (task_id,)).fetchone())

    def claim(self) -> dict[str, Any] | None:
        now = utc_now()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""
                SELECT * FROM tasks
                WHERE state IN ('QUEUED','RETRY') AND available_at <= ?
                ORDER BY created_at LIMIT 1
            """, (now,)).fetchone()
            if row is None:
                return None
            changed = db.execute("""
                UPDATE tasks SET state='RUNNING', attempts=attempts+1, updated_at=?
                WHERE task_id=? AND state IN ('QUEUED','RETRY')
            """, (now, row["task_id"])).rowcount
            if changed != 1:
                return None
            self._audit(db, row["task_id"], "TASK_CLAIMED", "worker",
                        {"attempt": row["attempts"] + 1})
            claimed = dict(db.execute("SELECT * FROM tasks WHERE task_id=?",
                                      (row["task_id"],)).fetchone())
            claimed["payload"] = json.loads(claimed["payload"])
            return claimed

    def finish(self, task_id: str, result: dict[str, Any], state: str = "SUCCEEDED") -> None:
        if state not in TERMINAL_STATES:
            raise ValueError(f"Unsupported terminal state: {state}")
        now = utc_now()
        with self._connect() as db:
            changed = db.execute("""
                UPDATE tasks SET state=?, result=?, last_error=NULL, updated_at=?
                WHERE task_id=? AND state='RUNNING'
            """, (state, json.dumps(result, ensure_ascii=False, sort_keys=True), now, task_id)).rowcount
            if changed != 1:
                raise ValueError("Task is not RUNNING or does not exist")
            self._audit(db, task_id, "TASK_" + state, "worker",
                        {"result_keys": sorted(result)})

    def complete(self, task_id: str, result: dict[str, Any]) -> None:
        self.finish(task_id, result, "SUCCEEDED")

    def fail(self, task_id: str, error: str, retry_delay_seconds: int = 30) -> str:
        now = utc_now()
        with self._connect() as db:
            row = db.execute("SELECT attempts,max_attempts FROM tasks WHERE task_id=? AND state='RUNNING'",
                             (task_id,)).fetchone()
            if row is None:
                raise ValueError("Task is not RUNNING or does not exist")
            state = "RETRY" if row["attempts"] < row["max_attempts"] else "FAILED"
            available = datetime.now(timezone.utc).timestamp() + max(0, retry_delay_seconds)
            retry_at = datetime.fromtimestamp(available, timezone.utc).isoformat()
            db.execute("UPDATE tasks SET state=?,last_error=?,available_at=?,updated_at=? WHERE task_id=?",
                       (state, error[:2000], retry_at, now, task_id))
            self._audit(db, task_id, "TASK_" + state, "worker",
                        {"error": error[:500], "attempt": row["attempts"]})
            return state

    def get(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if not row:
                return None
            item = dict(row)
            item["payload"] = json.loads(item["payload"])
            item["result"] = json.loads(item["result"]) if item["result"] else None
            return item

    def audit(self, task_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as db:
            if task_id:
                rows = db.execute("SELECT * FROM audit_events WHERE task_id=? ORDER BY event_id",
                                  (task_id,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM audit_events ORDER BY event_id").fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def _audit(db: sqlite3.Connection, task_id: str, event_type: str,
               actor: str, details: dict[str, Any]) -> None:
        db.execute("INSERT INTO audit_events(task_id,event_type,actor,details,created_at) VALUES(?,?,?,?,?)",
                   (task_id, event_type, actor, json.dumps(details, ensure_ascii=False, sort_keys=True), utc_now()))
