"""Policy-gated orchestration for the three independent Pulpos."""
from dataclasses import dataclass
from typing import Any

from core.permissions import AgentPermissions

PULPOS = ("ALPHA", "BETA", "GAMMA")
FORBIDDEN_FLAGS = ("spend", "transfer_out", "withdraw", "purchase", "investment_order")


@dataclass
class Task:
    task_id: str
    pulpo: str
    vertical: str
    payload: dict[str, Any]
    state: str = "DISCOVERED"


class Orchestrator:
    def __init__(self, workers: dict[str, Any] | None = None,
                 permissions: AgentPermissions | None = None):
        self.workers = workers or {}
        self.permissions = permissions or AgentPermissions()

    def dispatch(self, task: Task) -> Any:
        if task.pulpo not in PULPOS:
            raise ValueError(f"Unknown Pulpo: {task.pulpo}")

        # Reject explicit money-out or broker-order intents before any worker runs.
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

        worker = self.workers.get(task.pulpo)
        if worker is None:
            task.state = "BLOCKED"
            return {"task_id": task.task_id, "state": task.state,
                    "reason": "worker_not_registered"}
        return worker.run(task)
