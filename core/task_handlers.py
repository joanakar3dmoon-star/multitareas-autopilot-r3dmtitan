"""Deterministic, local-only handlers for selected catalog tasks."""
from __future__ import annotations
import math
import re
from datetime import datetime
from typing import Any

def _missing(payload: dict, fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in payload or payload[field] is None]

def _minor(payload: dict, field: str, default: int | None = None) -> int:
    value = payload.get(field, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer in minor currency units")
    return value

def _currency(payload: dict) -> str:
    value = payload.get("currency")
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z]{3}", value):
        raise ValueError("currency must be a three-letter code")
    return value.upper()

def _record_sources(task, _spec):
    sources = task.payload.get("source_refs")
    if not isinstance(sources, list) or not sources:
        return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                "reason": "source_refs_required", "missing_required_inputs": ["source_refs"]}
    if len(sources) > 50:
        return {"task_id": task.task_id, "state": "BLOCKED", "reason": "too_many_sources"}
    validated = []
    for item in sources:
        if not isinstance(item, dict):
            return {"task_id": task.task_id, "state": "BLOCKED", "reason": "source_reference_must_be_object"}
        url, provider, observed = item.get("url"), item.get("provider_id"), item.get("observed_at")
        if not isinstance(url, str) or not url.startswith("https://") or not isinstance(provider, str) or not provider.strip():
            return {"task_id": task.task_id, "state": "BLOCKED", "reason": "source_url_or_provider_invalid"}
        try:
            datetime.fromisoformat(str(observed).replace("Z", "+00:00"))
        except ValueError:
            return {"task_id": task.task_id, "state": "BLOCKED", "reason": "source_timestamp_invalid"}
        validated.append({"url": url, "provider_id": provider.strip()[:120], "observed_at": observed})
    return {"task_id": task.task_id, "state": "SUCCEEDED",
            "result": {"status": "STRUCTURE_VALIDATED", "source_count": len(validated),
                       "sources": validated, "remote_fetch_performed": False,
                       "license_verified": False}}

def _score_opportunity(task, _spec):
    payload = task.payload
    records = payload.get("validated_records")
    evidence = payload.get("evidence")
    if not isinstance(records, list) or not records or not isinstance(evidence, list) or not evidence:
        return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                "reason": "validated_records_and_evidence_required",
                "missing_required_inputs": ["validated_records", "evidence"]}
    if len(records) > 100:
        return {"task_id": task.task_id, "state": "BLOCKED", "reason": "too_many_records"}
    scored = []
    keys = ("demand_score", "evidence_score", "unit_economics_score", "risk_score")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            return {"task_id": task.task_id, "state": "BLOCKED", "reason": "record_must_be_object"}
        values = [item.get(key) for key in keys]
        invalid = [keys[i] for i, value in enumerate(values)
                   if not isinstance(value, (int, float)) or isinstance(value, bool)
                   or not math.isfinite(value) or not 0 <= value <= 100]
        if invalid:
            return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                    "reason": "explicit_component_scores_required", "missing_or_invalid_inputs": invalid}
        demand, evidence_quality, unit_economics, risk = values
        score = round(0.30 * demand + 0.25 * evidence_quality +
                      0.25 * unit_economics + 0.20 * (100 - risk), 2)
        scored.append({"record_id": str(item.get("record_id", index))[:100],
                       "score": score, "components": dict(zip(keys, values))})
    scored.sort(key=lambda row: row["score"], reverse=True)
    return {"task_id": task.task_id, "state": "HUMAN_REVIEW",
            "result": {"status": "RANKED_FROM_SUPPLIED_SCORES", "formula_version": "1.0",
                       "formula": "0.30*demand + 0.25*evidence + 0.25*unit_economics + 0.20*(100-risk)",
                       "records": scored, "evidence_count": len(evidence),
                       "external_sources_verified": False, "revenue_confirmed": False}}

def _calculate_total_price(task, _spec):
    payload = task.payload
    if "product_minor" not in payload:
        return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                "reason": "product_minor_required", "missing_required_inputs": ["product_minor"]}
    currency = _currency(payload)
    product = _minor(payload, "product_minor")
    shipping = _minor(payload, "shipping_minor", 0)
    tax = _minor(payload, "tax_minor", 0)
    fees = _minor(payload, "fees_minor", 0)
    return {"task_id": task.task_id, "state": "SUCCEEDED",
            "result": {"currency": currency, "product_minor": product,
                       "shipping_minor": shipping, "tax_minor": tax, "fees_minor": fees,
                       "total_minor": product + shipping + tax + fees,
                       "source": "supplied_inputs", "checkout_created": False}}

def _net_after_reserves(task, _spec):
    payload = task.payload
    fields = ("confirmed_cash_minor", "vat_reserved_minor", "tax_reserved_minor",
              "fees_minor", "refunds_reserved_minor", "committed_costs_minor",
              "emergency_reserve_minor")
    missing = _missing(payload, fields)
    if missing:
        return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                "reason": "cash_and_reserve_inputs_required", "missing_required_inputs": missing}
    currency = _currency(payload)
    values = {field: _minor(payload, field) for field in fields}
    pending = _minor(payload, "pending_cash_minor", 0)
    obligations = sum(values[field] for field in fields if field != "confirmed_cash_minor")
    net = values["confirmed_cash_minor"] - obligations
    result = {"currency": currency, **values, "pending_cash_excluded_minor": pending,
              "net_after_obligations_minor": net,
              "potential_available_minor": max(0, net),
              "shortfall_minor": max(0, -net),
              "uses_only_confirmed_cash": True}
    state = "HUMAN_REVIEW" if task.task_key == "calculate_potential_available_capital" else "SUCCEEDED"
    result["status"] = "PROPOSAL_REQUIRES_OWNER_REVIEW" if state == "HUMAN_REVIEW" else "INTERNAL_CALCULATION"
    result["investment_order_allowed"] = False
    return {"task_id": task.task_id, "state": state, "result": result}

def _separate_cash(task, _spec):
    payload = task.payload
    missing = _missing(payload, ("confirmed_cash_minor", "pending_cash_minor"))
    if missing:
        return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                "reason": "cash_inputs_required", "missing_required_inputs": missing}
    currency = _currency(payload)
    confirmed = _minor(payload, "confirmed_cash_minor")
    pending = _minor(payload, "pending_cash_minor")
    return {"task_id": task.task_id, "state": "SUCCEEDED",
            "result": {"currency": currency, "confirmed_cash_minor": confirmed,
                       "pending_cash_minor": pending, "pending_is_available_cash": False}}

class _Handler:
    def __init__(self, function):
        self.function = function
    def run(self, task, spec):
        return self.function(task, spec)

def build_task_handlers() -> dict[tuple[str, str, str], Any]:
    return {
        ("ALPHA", "market_intelligence", "record_sources"): _Handler(_record_sources),
        ("ALPHA", "market_intelligence", "score_opportunity"): _Handler(_score_opportunity),
        ("BETA", "merchandising", "calculate_total_price"): _Handler(_calculate_total_price),
        ("BETA", "treasury_controls", "calculate_net_after_reserves"): _Handler(_net_after_reserves),
        ("GAMMA", "capital_reserves", "separate_confirmed_and_pending_cash"): _Handler(_separate_cash),
        ("GAMMA", "capital_reserves", "calculate_potential_available_capital"): _Handler(_net_after_reserves),
    }
