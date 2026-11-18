"""Compatibility facade over the hardened Multifunción bridge transport.

Uses the receiver's actual contract: X-Pulpo-Token, worker, Idempotency-Key,
HTTPS-only transport and redirect refusal. The feature flag remains mandatory.
"""
from __future__ import annotations
import os
from connectors.bridge.multifuncion import MultifuncionBridge

class MultifuncionClient:
    def __init__(self, *, enabled: bool | None = None, base_url: str | None = None,
                 token: str | None = None, timeout: float = 5.0):
        flag_enabled = os.getenv("MULTIFUNCION_BRIDGE_ENABLED", "0") == "1"
        if enabled is True and not flag_enabled:
            raise ValueError("MULTIFUNCION_BRIDGE_ENABLED=1 is required")
        self.enabled = flag_enabled and enabled is not False
        self.bridge = MultifuncionBridge(base_url=base_url, api_token=token)
        if self.enabled and not self.bridge.configured:
            raise ValueError("Multifunción bridge URL and token are required")
        self.timeout = min(max(float(timeout), 1.0), 10.0)

    def create_job(self, pulpo: str, task_type: str, payload: dict,
                   idempotency_key: str) -> dict:
        if not self.enabled:
            return {"state": "DISABLED", "created": False}
        return self.bridge.enqueue(pulpo, task_type, payload, idempotency_key)
