"""Signed asynchronous event bridge to Cerebro; disabled until explicitly configured."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
from urllib.parse import urljoin
from connectors.bridge.transport import request_json, validate_base_url, validate_path

CONTRACT = "r3dm-cerebro-bridge-v1"
SOURCE = "multitareas-autopilot-r3dmtitan"

class CerebroBridge:
    def __init__(self, base_url: str | None = None, shared_secret: str | None = None,
                 events_path: str | None = None, health_path: str | None = None):
        self.base_url = (base_url if base_url is not None else os.getenv("CEREBRO_BASE_URL", "")).strip()
        self.secret = shared_secret if shared_secret is not None else os.getenv("CEREBRO_SHARED_SECRET", "")
        # The event route must be explicitly supplied; no unverified endpoint is guessed.
        self.events_path = (events_path if events_path is not None else os.getenv("CEREBRO_EVENTS_PATH", "")).strip()
        self.health_path = (health_path if health_path is not None else os.getenv("CEREBRO_HEALTH_PATH", "/health")).strip()
        if self.base_url:
            self.base_url = validate_base_url(self.base_url)
        if self.events_path:
            validate_path(self.events_path)
        if self.health_path:
            validate_path(self.health_path)

    @property
    def configured(self) -> bool:
        return bool(self.base_url and len(self.secret) >= 32 and self.events_path)

    @staticmethod
    def signature(body: bytes, secret: str) -> str:
        return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    def handshake(self) -> dict:
        if not self.configured:
            return {"configured": False, "connected": False,
                    "reason": "CEREBRO_BASE_URL, CEREBRO_SHARED_SECRET (32+ chars) and CEREBRO_EVENTS_PATH required"}
        try:
            health = request_json(urljoin(self.base_url + "/", self.health_path.lstrip("/")),
                                  timeout=8)
            return {"configured": True, "connected": True, "contract": CONTRACT,
                    "remote_health": health}
        except Exception as exc:
            return {"configured": True, "connected": False, "contract": CONTRACT,
                    "reason": str(exc)[:300]}

    def deliver(self, event: dict) -> tuple[bool, str | None]:
        if not self.configured:
            return False, "bridge_not_configured"
        if not isinstance(event, dict) or not event.get("event_id"):
            return False, "invalid_event_envelope"
        envelope = {"contract": CONTRACT, "source": SOURCE, "event": event}
        body = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-R3DM-Signature": self.signature(body, self.secret),
            "X-R3DM-Contract": CONTRACT,
            "Idempotency-Key": str(event["event_id"]),
        }
        try:
            request_json(urljoin(self.base_url + "/", self.events_path.lstrip("/")),
                         method="POST", payload=envelope, headers=headers, timeout=15)
            return True, None
        except Exception as exc:
            return False, str(exc)[:500]
