"""Append-only inbound receipt ledger; callers must verify provider signatures first."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any
from core.store import utc_now

class InboundReceiptLedger:
    def __init__(self, database: str = "data/multitareas.db"):
        if database == ":memory:":
            raise ValueError("InboundReceiptLedger requires a file-backed database")
        self.database = database
        Path(database).parent.mkdir(parents=True, exist_ok=True)
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
        """Record a previously signature-verified event; this method does not verify signatures."""
        if not isinstance(provider, str) or not provider.strip() or not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("provider and event_id are required")
        if not isinstance(amount_minor, int) or isinstance(amount_minor, bool) or amount_minor < 0:
            raise ValueError("amount_minor must be a non-negative integer")
        if not isinstance(currency, str):
            raise ValueError("currency must be a three-letter code")
        code = currency.upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError("currency must be a three-letter code")
        safe_metadata = metadata or {}
        if not isinstance(safe_metadata, dict):
            raise ValueError("metadata must be an object")
        encoded_metadata = json.dumps(safe_metadata, ensure_ascii=False, sort_keys=True)
        if len(encoded_metadata) > 4000:
            raise ValueError("metadata exceeds 4k characters")
        with sqlite3.connect(self.database) as db:
            cur = db.execute("""INSERT OR IGNORE INTO inbound_receipts
                (provider,provider_event_id,amount_minor,currency,received_at,metadata)
                VALUES(?,?,?,?,?,?)""",
                (provider.strip(), event_id.strip(), amount_minor, code, utc_now(), encoded_metadata))
            return cur.rowcount == 1

    def list_pending(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(
                "SELECT * FROM inbound_receipts WHERE status='PENDING_RECONCILIATION' ORDER BY received_at")]
