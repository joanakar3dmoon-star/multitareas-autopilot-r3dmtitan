"""Drain the durable Cerebro event outbox with bounded retry backoff."""
from __future__ import annotations
from core.store import TaskStore
from connectors.bridge.cerebro import CerebroBridge

class BridgeDispatcher:
    def __init__(self, store: TaskStore, cerebro: CerebroBridge | None = None):
        self.store = store
        self.cerebro = cerebro or CerebroBridge()

    def dispatch_pending(self, limit: int = 20) -> dict:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        if not self.cerebro.configured:
            return {"configured": False, "sent": 0, "pending": None,
                    "reason": "Cerebro bridge not configured; events remain in local outbox"}
        events = self.store.pending_bridge_events("cerebro", limit)
        pending_count = self.store.count_pending_bridge_events("cerebro")
        if not events:
            return {"configured": True, "connected": None, "sent": 0,
                    "pending": pending_count, "reason": "no_due_events"}
        health = self.cerebro.handshake()
        if not health.get("connected"):
            reason = health.get("reason", "handshake_failed")
            for row in events:
                self.store.mark_bridge_failed(row["event_id"], "cerebro", reason)
            return {"configured": True, "connected": False, "sent": 0,
                    "pending": pending_count, "reason": reason}
        sent = 0
        for row in events:
            event = {"event_id": row["event_id"], "event_type": row["event_type"],
                     "payload": row["payload"], "occurred_at": row["created_at"]}
            ok, error = self.cerebro.deliver(event)
            if ok:
                self.store.mark_bridge_delivered(row["event_id"], "cerebro")
                sent += 1
            else:
                self.store.mark_bridge_failed(row["event_id"], "cerebro", error or "delivery_failed")
        return {"configured": True, "connected": True, "sent": sent,
                "pending": self.store.count_pending_bridge_events("cerebro")}
