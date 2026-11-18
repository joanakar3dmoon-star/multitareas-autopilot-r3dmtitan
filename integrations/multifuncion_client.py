"""Opt-in client for the Superagente Multifunción Pulpo job API.

This adapter creates jobs only after explicit activation; it never submits money,
payment, customer, or unrestricted task data. API contract follows PR #4.
"""
from __future__ import annotations
import json
import os
import urllib.request

class MultifuncionClient:
    def __init__(self, *, enabled: bool | None = None, base_url: str | None = None,
                 token: str | None = None, timeout: float = 5.0):
        configured = os.getenv("MULTIFUNCION_BRIDGE_ENABLED", "0") == "1"
        self.enabled = configured if enabled is None else enabled
        self.base_url = (base_url or os.getenv("MULTIFUNCION_BASE_URL", "")).rstrip("/")
        self.token = token if token is not None else os.getenv("MULTIFUNCION_API_TOKEN", "")
        self.timeout = min(max(float(timeout), 1.0), 10.0)
        if self.enabled:
            if not self.base_url.startswith("https://"):
                raise ValueError("MULTIFUNCION_BASE_URL must use HTTPS")
            if len(self.token) < 32:
                raise ValueError("MULTIFUNCION_API_TOKEN must contain at least 32 characters")

    def create_job(self, pulpo: str, task_type: str, payload: dict,
                   idempotency_key: str) -> dict:
        if not self.enabled:
            return {"state": "DISABLED", "created": False}
        if pulpo not in {"ALPHA", "BETA", "GAMMA"}:
            raise ValueError("unknown Pulpo")
        if not isinstance(task_type, str) or not task_type.strip() or len(task_type) > 100:
            raise ValueError("invalid task_type")
        if not isinstance(payload, dict) or set(payload) - {"task_id", "vertical", "task_key", "input_ref"}:
            raise ValueError("payload contains disallowed fields")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
            raise ValueError("invalid Idempotency-Key")
        body = json.dumps({"pulpo": pulpo, "task_type": task_type, "payload": payload},
                          ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/api/pulpos/jobs", data=body, method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.token,
                     "Idempotency-Key": idempotency_key},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            if response.status not in (200, 201, 202):
                raise RuntimeError("Multifunción rejected job")
            return json.loads(response.read(8192).decode("utf-8"))
