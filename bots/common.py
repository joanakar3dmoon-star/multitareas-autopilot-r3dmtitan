"""Shared deterministic helpers for bot workers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class BotOutput:
    bot: str
    status: str
    data: dict[str, Any]
    warnings: tuple[str, ...] = ()

def require_mapping(value: Any, name: str = "payload") -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value

def non_empty_text(value: Any, name: str, max_length: int = 12000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    cleaned = value.strip()
    if len(cleaned) > max_length:
        raise ValueError(f"{name} exceeds {max_length} characters")
    return cleaned
