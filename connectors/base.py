"""Connector contracts and fail-closed disabled adapter."""
from __future__ import annotations
from typing import Any, Protocol

class Connector(Protocol):
    name: str
    def healthcheck(self) -> dict[str, Any]: ...

class ConnectorDisabled(RuntimeError):
    pass

class DisabledConnector:
    def __init__(self, name: str, reason: str = "not_configured"):
        self.name, self.reason = name, reason
    def healthcheck(self):
        return {"name": self.name, "enabled": False, "reason": self.reason}
    def execute(self, *_args, **_kwargs):
        raise ConnectorDisabled(f"{self.name} is disabled: {self.reason}")
