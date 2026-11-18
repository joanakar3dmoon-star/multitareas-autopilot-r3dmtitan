"""Append-only inbound receipt ledger. No payout, refund or transfer operation exists here."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any
from core.store import utc_now
class InboundReceiptLedger:
    def __init__(self, database: str = "data/multitareas.db"):
        self.database = database
        if database != ":memory:": Path(database).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS inbound_receipts (
                provider TEXT NOT NULL, provider_event_id TEXT NOT NULL,
                amount_minor INTEGER NOT NULL CHECK(amount_minor >= 0),
                currency TEXT NOT NULL CHECK(length(currency)=3),
                status TEXT NOT NULL DEFAULT 'PENDING_RECONCILIATION',
                received_at TEXT NOT NULL, metadata TEXT NOT NULL DEFAULT '{}',
                PRIMARY KEY(provider, provider_event_id))""")
    def record_verified(self, provider: str, event_id: str, amount_minor: int,
                        currency: str, metadata: dict[str, Any] | None = None) -> bool:
        if not provider or not event_id or not isinstance(amount_minor, int) or amount_minor < 0: raise ValueError("provider, event_id and non-negative integer amount are required")
        code = currency.upper()
        if len(code) != 3 or not code.isalpha(): raise ValueError("currency must be a 3-letter code")
        with sqlite3.connect(self.database) as db:
            cur = db.execute("""INSERT OR IGNORE INTO inbound_receipts
                (provider,provider_event_id,amount_minor,currency,received_at,metadata)
                VALUES(?,?,?,?,?,?)""", (provider, event_id, amount_minor, code, utc_now(), json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)))
            return cur.rowcount == 1
    def list_pending(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT * FROM inbound_receipts WHERE status='PENDING_RECONCILIATION' ORDER BY received_at")]
