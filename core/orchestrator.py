"""Policy-gated orchestration for the three independent Pulpos."""
from dataclasses import dataclass
from typing import Any
from core.permissions import AgentPermissions
from core.catalog import TaskCatalog

PULPOS = ("ALPHA", "BETA", "GAMMA")
FORBIDDEN_FLAGS = (
    "spend", "transfer_out", "withdraw", "purchase", "buy", "subscribe",
    "payout", "refund", "send_money", "investment_order", "broker_order",
    "place_order", "execute_trade",
)

@dataclass
class Task:
    task_id: str
    pulpo: str
    vertical: str
    payload: dict[str, Any]
    state: str = "DISCOVERED"
    block: str | None = None
    task_key: str | None = None

class Orchestrator:
    def __init__(self, workers: dict[str, Any] | None = None,
                 permissions: AgentPermissions | None = None,
                 catalog: TaskCatalog | None = None,
                 task_handlers: dict[tuple[str, str, str], Any] | None = None):
        self.workers = workers or {}
        self.permissions = permissions or AgentPermissions()
        self.catalog = catalog or TaskCatalog()
        self.task_handlers = task_handlers or {}

    def dispatch(self, task: Task) -> Any:
        if task.pulpo not in PULPOS:
            raise ValueError(f"Unknown Pulpo: {task.pulpo}")
        if not isinstance(task.payload, dict):
            return {"task_id": task.task_id, "state": "BLOCKED",
                    "reason": "payload_must_be_object"}
        for flag in FORBIDDEN_FLAGS:
            if task.payload.get(flag) is True:
                return {"task_id": task.task_id, "state": "BLOCKED",
                        "reason": "financial_action_denied", "action": flag}
        requested_action = task.payload.get("requested_action")
        if requested_action:
            try:
                self.permissions.require(str(requested_action))
            except PermissionError:
                return {"task_id": task.task_id, "state": "BLOCKED",
                        "reason": "permission_denied", "action": str(requested_action)}

        block = task.block or task.payload.get("block")
        task_key = task.task_key or task.payload.get("task_key")
        if block is not None or task_key is not None:
            if not isinstance(block, str) or not isinstance(task_key, str):
                return {"task_id": task.task_id, "state": "BLOCKED",
                        "reason": "block_and_task_key_required"}
            spec = self.catalog.get_task(task.pulpo, block, task_key)
            if spec is None:
                return {"task_id": task.task_id, "state": "BLOCKED",
                        "reason": "task_not_in_catalog", "block": block, "task_key": task_key}
            required = spec.get("required_inputs", [])
            missing = [field for field in required
                       if field != "job_id" and not task.payload.get(field)]
            if missing:
                return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                        "reason": "required_inputs_missing", "block": block,
                        "task_key": task_key, "missing_required_inputs": missing}
            handler = self.task_handlers.get((task.pulpo, block, task_key))
            if handler is None:
                return {"task_id": task.task_id, "state": "NEEDS_ADAPTER",
                        "reason": "task_handler_not_registered", "catalog_version": self.catalog.version,
                        "block": block, "task_key": task_key, "required_inputs": required,
                        "missing_required_inputs": [],
                        "execution_mode": spec.get("execution_mode", "connector_required_or_awaiting_connector")}
            return handler.run(task, spec)

        worker = self.workers.get(task.pulpo)
        if worker is None:
            task.state = "BLOCKED"
            return {"task_id": task.task_id, "state": task.state,
                    "reason": "worker_not_registered"}
        return worker.run(task)
