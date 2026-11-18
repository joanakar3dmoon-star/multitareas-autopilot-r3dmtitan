"""Deterministic worker loop over the durable task queue."""
from __future__ import annotations
from typing import Any
from core.store import TaskStore, TERMINAL_STATES
from core.orchestrator import Orchestrator, Task

class WorkerRuntime:
    def __init__(self, store: TaskStore, orchestrator: Orchestrator) -> None:
        self.store = store
        self.orchestrator = orchestrator

    def enqueue(self, task_id: str, pulpo: str, vertical: str,
                payload: dict[str, Any], idempotency_key: str | None = None) -> dict[str, Any]:
        if pulpo not in ("ALPHA", "BETA", "GAMMA"):
            raise ValueError("Unknown Pulpo")
        return self.store.enqueue(task_id, pulpo, vertical, payload, idempotency_key)

    def run_once(self) -> dict[str, Any] | None:
        record = self.store.claim()
        if record is None:
            return None
        payload = record["payload"]
        task = Task(record["task_id"], record["pulpo"], record["vertical"], payload,
                    "RUNNING", payload.get("block"), payload.get("task_key"))
        try:
            outcome = self.orchestrator.dispatch(task)
            if not isinstance(outcome, dict):
                raise TypeError("Worker must return a dictionary result")
            requested_state = outcome.get("state")
            # Never infer success from an unknown or merely descriptive worker state.
            final_state = requested_state if requested_state in TERMINAL_STATES else "HUMAN_REVIEW"
            self.store.finish(task.task_id, outcome, final_state)
            return {"task_id": task.task_id, "state": final_state, "outcome": outcome}
        except Exception as exc:
            state = self.store.fail(task.task_id, f"{type(exc).__name__}: {exc}")
            return {"task_id": task.task_id, "state": state, "error": str(exc)}

    def run_batch(self, limit: int = 10) -> list[dict[str, Any]]:
        if limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500")
        results = []
        for _ in range(limit):
            result = self.run_once()
            if result is None:
                break
            results.append(result)
        return results
