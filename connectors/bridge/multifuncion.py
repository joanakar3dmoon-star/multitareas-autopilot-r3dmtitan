"""Explicit job handoff to the separate Superagente Multifunción API."""
from __future__ import annotations
import json
import os
import re
from urllib.parse import urljoin
from connectors.bridge.transport import request_json, validate_base_url, validate_path

SENSITIVE_KEYS = {"password", "secret", "api_key", "access_token", "refresh_token",
                  "iban", "account_number", "card_number", "cvv", "email", "phone"}

def _reject_sensitive(value, path="payload"):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                raise ValueError(f"sensitive field is not allowed in bridge payload: {path}.{key}")
            _reject_sensitive(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]")

class MultifuncionBridge:
    """Targets the /api/pulpos/jobs contract in Multifunción PR #4; not assumed deployed."""
    def __init__(self, base_url: str | None = None, api_token: str | None = None,
                 jobs_path: str | None = None, health_path: str | None = None,
                 enabled: bool | None = None):
        self.base_url = (base_url if base_url is not None else os.getenv("MULTIFUNCION_BASE_URL", "")).strip()
        self.token = api_token if api_token is not None else os.getenv("MULTIFUNCION_API_TOKEN", "")
        self.jobs_path = (jobs_path if jobs_path is not None else os.getenv("MULTIFUNCION_JOBS_PATH", "/api/pulpos/jobs")).strip()
        self.health_path = (health_path if health_path is not None else os.getenv("MULTIFUNCION_HEALTH_PATH", "/api/pulpos/health")).strip()
        self.enabled = (os.getenv("MULTIFUNCION_BRIDGE_ENABLED", "0") == "1") if enabled is None else enabled
        if self.base_url:
            self.base_url = validate_base_url(self.base_url)
        validate_path(self.jobs_path)
        validate_path(self.health_path)

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.base_url and len(self.token) >= 32)

    def healthcheck(self) -> dict:
        if not self.configured:
            return {"configured": False, "connected": False,
                    "reason": "MULTIFUNCION_BRIDGE_ENABLED=1, MULTIFUNCION_BASE_URL and MULTIFUNCION_API_TOKEN (32+ chars) required"}
        try:
            data = request_json(urljoin(self.base_url + "/", self.health_path.lstrip("/")), timeout=8)
            return {"configured": True, "connected": True, "remote_health": data}
        except Exception as exc:
            return {"configured": True, "connected": False, "reason": str(exc)[:300]}

    def enqueue(self, pulpo: str, worker: str, payload: dict,
                idempotency_key: str) -> dict:
        if not self.configured:
            raise PermissionError("Multifunción bridge is disabled or not configured")
        if pulpo not in {"ALPHA", "BETA", "GAMMA"}:
            raise ValueError("unknown pulpo")
        if not isinstance(worker, str) or not re.fullmatch(r"[a-zA-Z0-9_.:-]{1,100}", worker):
            raise ValueError("invalid worker name")
        if not isinstance(payload, dict) or len(json.dumps(payload, ensure_ascii=False)) > 16000:
            raise ValueError("payload must be an object under 16k characters")
        _reject_sensitive(payload)
        if not isinstance(idempotency_key, str) or not re.fullmatch(r"[a-zA-Z0-9_.:-]{8,120}", idempotency_key):
            raise ValueError("idempotency_key must be 8-120 safe characters")
        headers = {"Content-Type": "application/json", "X-Pulpo-Token": self.token,
                   "Idempotency-Key": idempotency_key}
        body = {"pulpo": pulpo, "worker": worker, "payload": payload}
        return request_json(urljoin(self.base_url + "/", self.jobs_path.lstrip("/")),
                            method="POST", payload=body, headers=headers, timeout=15)
