"""Versioned outbound contracts for R3DM project bridges.

No bridge is enabled by default. This module never transfers money or task payloads.
"""
from __future__ import annotations

CONTRACT = "r3dm-cerebro-bridge-v1"
SOURCE = "multitareas-autopilot-r3dmtitan"
CEREBRO_EVENT_PATH = "/api/integraciones/multitareas/events"
CEREBRO_HEALTH_PATH = "/api/integraciones/multitareas/health"
CEREBRO_ALLOWED_EVENT = "task.state_changed"
CEREBRO_ALLOWED_STATES = {
    "QUEUED", "RUNNING", "RETRY", "FAILED", "SUCCEEDED", "BLOCKED",
    "HUMAN_REVIEW", "RESEARCH_ONLY", "NEEDS_ADAPTER",
}
PULPOS = {"ALPHA", "BETA", "GAMMA"}

def build_cerebro_envelope(event: dict) -> dict:
    """Return only the strict status payload accepted by QUASAR's PR #123."""
    if not isinstance(event, dict) or event.get("event_type") != CEREBRO_ALLOWED_EVENT:
        raise ValueError("unsupported Cerebro event")
    payload = event.get("payload")
    if not isinstance(payload, dict) or set(payload) != {"task_id", "pulpo", "vertical", "state"}:
        raise ValueError("invalid Cerebro status payload")
    if payload["pulpo"] not in PULPOS or payload["state"] not in CEREBRO_ALLOWED_STATES:
        raise ValueError("invalid Pulpo or state")
    for key in ("task_id", "vertical"):
        if not isinstance(payload[key], str) or not payload[key].strip() or len(payload[key]) > 120:
            raise ValueError(f"invalid {key}")
    return {
        "contract": CONTRACT,
        "source": SOURCE,
        "event": {
            "event_id": event["event_id"],
            "event_type": CEREBRO_ALLOWED_EVENT,
            "payload": {key: payload[key] for key in ("task_id", "pulpo", "vertical", "state")},
            "occurred_at": event["created_at"],
        },
    }
