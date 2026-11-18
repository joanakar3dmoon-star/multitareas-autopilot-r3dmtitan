"""SQLite persistence for tasks, audit events and the durable bridge outbox."""
from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

TERMINAL_STATES = {"SUCCEEDED", "BLOCKED", "HUMAN_REVIEW", "RESEARCH_ONLY", "NEEDS_ADAPTER"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class TaskStore:
    """Durable SQLite queue with atomic claims, leases and append-only audit/outbox."""
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
                    task_id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE,
                    pulpo TEXT NOT NULL, vertical TEXT NOT NULL, payload TEXT NOT NULL,
                    state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3, available_at TEXT NOT NULL,
                    lease_until TEXT, result TEXT, last_error TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_ready ON tasks(state, available_at, created_at);
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT,
                    event_type TEXT NOT NULL, actor TEXT NOT NULL, details TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(task_id)
                );
                CREATE TABLE IF NOT EXISTS bridge_outbox (
                    event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bridge_deliveries (
                    event_id TEXT NOT NULL, destination TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'PENDING', attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt_at TEXT NOT NULL, last_error TEXT, delivered_at TEXT,
                    PRIMARY KEY(event_id,destination),
                    FOREIGN KEY(event_id) REFERENCES bridge_outbox(event_id)
                );
                CREATE INDEX IF NOT EXISTS idx_bridge_pending
                    ON bridge_deliveries(destination,state,next_attempt_at);
            """)
            columns = {row["name"] for row in db.execute("PRAGMA table_info(tasks)")}
            if "lease_until" not in columns:
                db.execute("ALTER TABLE tasks ADD COLUMN lease_until TEXT")

    def enqueue(self, task_id: str, pulpo: str, vertical: str,
                payload: dict[str, Any], idempotency_key: str | None = None,
                max_attempts: int = 3) -> dict[str, Any]:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("task_id is required")
        if not isinstance(pulpo, str) or not pulpo.strip() or not isinstance(vertical, str) or not vertical.strip():
            raise ValueError("pulpo and vertical are required")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        now = utc_now()
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
            raise ValueError("max_attempts must be an integer >= 1")
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

    def claim(self, lease_seconds: int = 900) -> dict[str, Any] | None:
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) or not 30 <= lease_seconds <= 3600:
            raise ValueError("lease_seconds must be an integer between 30 and 3600")
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        lease_until = (now_dt + timedelta(seconds=lease_seconds)).isoformat()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            expired = db.execute("""
                SELECT task_id,attempts,max_attempts,pulpo,vertical FROM tasks
                WHERE state='RUNNING' AND (lease_until IS NULL OR lease_until <= ?)
            """, (now,)).fetchall()
            for row in expired:
                state = "RETRY" if row["attempts"] < row["max_attempts"] else "FAILED"
                db.execute("""
                    UPDATE tasks SET state=?,lease_until=NULL,available_at=?,last_error=?,
                                     updated_at=? WHERE task_id=? AND state='RUNNING'
                """, (state, now, "worker_lease_expired", now, row["task_id"]))
                self._audit(db, row["task_id"], "TASK_LEASE_EXPIRED", "runtime",
                            {"attempt": row["attempts"], "resulting_state": state})
                self._queue_bridge_event(db, "task.state_changed",
                    {"task_id": row["task_id"], "pulpo": row["pulpo"],
                     "vertical": row["vertical"], "state": state})
            row = db.execute("""
                SELECT * FROM tasks
                WHERE state IN ('QUEUED','RETRY') AND available_at <= ?
                ORDER BY created_at LIMIT 1
            """, (now,)).fetchone()
            if row is None:
                return None
            changed = db.execute("""
                UPDATE tasks SET state='RUNNING', attempts=attempts+1,
                                 lease_until=?, updated_at=?
                WHERE task_id=? AND state IN ('QUEUED','RETRY')
            """, (lease_until, now, row["task_id"])).rowcount
            if changed != 1:
                return None
            self._audit(db, row["task_id"], "TASK_CLAIMED", "worker",
                        {"attempt": row["attempts"] + 1, "lease_until": lease_until})
            claimed = dict(db.execute("SELECT * FROM tasks WHERE task_id=?",
                                      (row["task_id"],)).fetchone())
            claimed["payload"] = json.loads(claimed["payload"])
            return claimed

    def renew_lease(self, task_id: str, lease_seconds: int = 900) -> bool:
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) or not 30 <= lease_seconds <= 3600:
            raise ValueError("lease_seconds must be an integer between 30 and 3600")
        now_dt = datetime.now(timezone.utc)
        with self._connect() as db:
            changed = db.execute("""
                UPDATE tasks SET lease_until=?,updated_at=?
                WHERE task_id=? AND state='RUNNING'
            """, ((now_dt + timedelta(seconds=lease_seconds)).isoformat(),
                  now_dt.isoformat(), task_id)).rowcount
            if changed:
                self._audit(db, task_id, "TASK_LEASE_RENEWED", "worker",
                            {"lease_seconds": lease_seconds})
            return changed == 1

    def finish(self, task_id: str, result: dict[str, Any], state: str = "SUCCEEDED") -> None:
        if state not in TERMINAL_STATES:
            raise ValueError(f"Unsupported terminal state: {state}")
        now = utc_now()
        with self._connect() as db:
            row = db.execute("SELECT pulpo,vertical FROM tasks WHERE task_id=? AND state='RUNNING'",
                             (task_id,)).fetchone()
            if row is None:
                raise ValueError("Task is not RUNNING or does not exist")
            changed = db.execute("""
                UPDATE tasks SET state=?, result=?, last_error=NULL, lease_until=NULL, updated_at=?
                WHERE task_id=? AND state='RUNNING'
            """, (state, json.dumps(result, ensure_ascii=False, sort_keys=True), now, task_id)).rowcount
            if changed != 1:
                raise ValueError("Task is not RUNNING or does not exist")
            self._audit(db, task_id, "TASK_" + state, "worker",
                        {"result_keys": sorted(result)})
            self._queue_bridge_event(db, "task.state_changed",
                {"task_id": task_id, "pulpo": row["pulpo"],
                 "vertical": row["vertical"], "state": state})

    def complete(self, task_id: str, result: dict[str, Any]) -> None:
        self.finish(task_id, result, "SUCCEEDED")

    def fail(self, task_id: str, error: str, retry_delay_seconds: int = 30) -> str:
        now = utc_now()
        with self._connect() as db:
            row = db.execute("SELECT attempts,max_attempts,pulpo,vertical FROM tasks WHERE task_id=? AND state='RUNNING'",
                             (task_id,)).fetchone()
            if row is None:
                raise ValueError("Task is not RUNNING or does not exist")
            state = "RETRY" if row["attempts"] < row["max_attempts"] else "FAILED"
            available = datetime.now(timezone.utc).timestamp() + max(0, retry_delay_seconds)
            retry_at = datetime.fromtimestamp(available, timezone.utc).isoformat()
            db.execute("UPDATE tasks SET state=?,last_error=?,lease_until=NULL,available_at=?,updated_at=? WHERE task_id=?",
                       (state, error[:2000], retry_at, now, task_id))
            self._audit(db, task_id, "TASK_" + state, "worker",
                        {"error": error[:500], "attempt": row["attempts"]})
            self._queue_bridge_event(db, "task.state_changed",
                {"task_id": task_id, "pulpo": row["pulpo"],
                 "vertical": row["vertical"], "state": state})
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

    def pending_bridge_events(self, destination: str = "cerebro", limit: int = 20) -> list[dict[str, Any]]:
        if destination != "cerebro":
            raise ValueError("unsupported bridge destination")
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        now = utc_now()
        with self._connect() as db:
            rows = db.execute("""
                SELECT o.event_id,o.event_type,o.payload,o.created_at,d.attempts
                FROM bridge_outbox o JOIN bridge_deliveries d USING(event_id)
                WHERE d.destination=? AND d.state='PENDING' AND d.next_attempt_at<=?
                ORDER BY o.created_at LIMIT ?
            """, (destination, now, limit)).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["payload"] = json.loads(item["payload"])
                result.append(item)
            return result

    def mark_bridge_delivered(self, event_id: str, destination: str) -> None:
        now = utc_now()
        with self._connect() as db:
            changed = db.execute("""
                UPDATE bridge_deliveries SET state='DELIVERED',delivered_at=?,last_error=NULL
                WHERE event_id=? AND destination=? AND state='PENDING'
            """, (now, event_id, destination)).rowcount
            if changed != 1:
                raise ValueError("bridge delivery is not pending")

    def mark_bridge_failed(self, event_id: str, destination: str, error: str) -> None:
        with self._connect() as db:
            row = db.execute("SELECT attempts FROM bridge_deliveries WHERE event_id=? AND destination=? AND state='PENDING'",
                             (event_id, destination)).fetchone()
            if row is None:
                raise ValueError("bridge delivery is not pending")
            attempts = row["attempts"] + 1
            delay = min(3600, 5 * (2 ** min(attempts, 9)))
            retry_at = (datetime.now(timezone.utc) + timedelta(seconds=delay)).isoformat()
            db.execute("""
                UPDATE bridge_deliveries SET attempts=?,next_attempt_at=?,last_error=?
                WHERE event_id=? AND destination=? AND state='PENDING'
            """, (attempts, retry_at, str(error)[:500], event_id, destination))

    def count_pending_bridge_events(self, destination: str = "cerebro") -> int:
        with self._connect() as db:
            return db.execute("SELECT COUNT(*) FROM bridge_deliveries WHERE destination=? AND state='PENDING'",
                              (destination,)).fetchone()[0]

    @staticmethod
    def _queue_bridge_event(db: sqlite3.Connection, event_type: str,
                            payload: dict[str, Any]) -> str:
        event_id = str(uuid.uuid4())
        now = utc_now()
        db.execute("INSERT INTO bridge_outbox(event_id,event_type,payload,created_at) VALUES(?,?,?,?)",
                   (event_id, event_type, json.dumps(payload, ensure_ascii=False, sort_keys=True), now))
        db.execute("""INSERT INTO bridge_deliveries(event_id,destination,state,attempts,next_attempt_at)
                      VALUES(?,'cerebro','PENDING',0,?)""", (event_id, now))
        return event_id

    @staticmethod
    def _audit(db: sqlite3.Connection, task_id: str, event_type: str,
               actor: str, details: dict[str, Any]) -> None:
        db.execute("INSERT INTO audit_events(task_id,event_type,actor,details,created_at) VALUES(?,?,?,?,?)",
                   (task_id, event_type, actor, json.dumps(details, ensure_ascii=False, sort_keys=True), utc_now()))
