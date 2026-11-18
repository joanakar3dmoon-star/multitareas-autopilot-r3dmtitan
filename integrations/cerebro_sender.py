"""Opt-in HMAC sender for the QUASAR/Cerebro status receiver.

Disabled unless MULTITAREAS_CEREBRO_BRIDGE_ENABLED=1 and all endpoint/secret
settings are present. Sends status only; never sends task payloads or PII.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from integrations.bridge_contracts import (
    CONTRACT, CEREBRO_EVENT_PATH, CEREBRO_HEALTH_PATH, build_cerebro_envelope,
)

class CerebroBridge:
    def __init__(self, store, *, enabled: bool | None = None,
                 base_url: str | None = None, secret: str | None = None,
                 timeout: float = 5.0):
        raw_enabled = os.getenv("MULTITAREAS_CEREBRO_BRIDGE_ENABLED", "0") == "1"
        self.enabled = raw_enabled if enabled is None else enabled
        self.base_url = (base_url or os.getenv("CEREBRO_BASE_URL", "")).rstrip("/")
        self.secret = secret if secret is not None else os.getenv("CEREBRO_SHARED_SECRET", "")
        self.store = store
        self.timeout = min(max(float(timeout), 1.0), 10.0)
        if self.enabled:
            if not self.base_url.startswith("https://"):
                raise ValueError("CEREBRO_BASE_URL must use HTTPS")
            if len(self.secret) < 32:
                raise ValueError("CEREBRO_SHARED_SECRET must contain at least 32 characters")

    def health(self) -> dict:
        if not self.enabled:
            return {"enabled": False, "state": "DISABLED"}
        request = urllib.request.Request(self.base_url + CEREBRO_HEALTH_PATH, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            if response.status != 200:
                raise RuntimeError("Cerebro health check failed")
            return json.loads(response.read(4096).decode("utf-8"))

    def deliver_once(self, limit: int = 20) -> dict:
        if not self.enabled:
            return {"enabled": False, "delivered": 0, "state": "DISABLED"}
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        delivered = 0
        for item in self.store.pending_bridge_events("cerebro", limit):
            try:
                envelope = build_cerebro_envelope(item)
                raw = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                signature = hmac.new(self.secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
                headers = {
                    "Content-Type": "application/json",
                    "X-R3DM-Contract": CONTRACT,
                    "X-R3DM-Signature": "sha256=" + signature,
                    "Idempotency-Key": item["event_id"],
                }
                request = urllib.request.Request(
                    self.base_url + CEREBRO_EVENT_PATH, data=raw, headers=headers, method="POST"
                )
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    result = json.loads(response.read(4096).decode("utf-8"))
                    if response.status != 200 or result.get("accepted") is not True:
                        raise RuntimeError("Cerebro did not accept event")
                self.store.mark_bridge_delivered(item["event_id"], "cerebro")
                delivered += 1
            except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError, OSError) as exc:
                self.store.mark_bridge_failed(item["event_id"], "cerebro", str(exc))
        return {"enabled": True, "delivered": delivered, "state": "PROCESSED"}
