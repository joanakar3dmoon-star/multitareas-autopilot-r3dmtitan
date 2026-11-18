"""Orquestación mínima y explícita de los tres Pulpos."""
from dataclasses import dataclass
from typing import Any

PULPOS = ("ALPHA", "BETA", "GAMMA")

@dataclass
class Task:
    task_id: str
    pulpo: str
    vertical: str
    payload: dict[str, Any]
    state: str = "DISCOVERED"

class Orchestrator:
    def __init__(self, workers: dict[str, Any] | None = None):
        self.workers = workers or {}

    def dispatch(self, task: Task) -> Any:
        if task.pulpo not in PULPOS:
            raise ValueError(f"Unknown Pulpo: {task.pulpo}")
        worker = self.workers.get(task.pulpo)
        if worker is None:
            task.state = "BLOCKED"
            return {"task_id": task.task_id, "state": task.state, "reason": "worker_not_registered"}
        return worker.run(task)
