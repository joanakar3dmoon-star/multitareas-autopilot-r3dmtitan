"""Versioned declarative task catalog for ALPHA, BETA and GAMMA."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class TaskCatalog:
    def __init__(self, path: str | None = None):
        self.path = Path(path) if path else Path(__file__).resolve().parents[1] / "specs" / "especificaciones_tareas.json"
        if not self.path.is_file():
            raise FileNotFoundError(f"task catalog not found: {self.path}")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("schema_version") != "1.0.0" or not isinstance(data.get("pulpos"), list):
            raise ValueError("unsupported or invalid task catalog schema")
        self.version = data.get("catalog_version", "unknown")
        self._tasks: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._counts: dict[str, int] = {}
        for pulpo in data["pulpos"]:
            pulpo_id = pulpo.get("id")
            if pulpo_id not in {"ALPHA", "BETA", "GAMMA"}:
                raise ValueError(f"invalid Pulpo in task catalog: {pulpo_id}")
            count = 0
            for block in pulpo.get("blocks", []):
                block_id = block.get("id")
                if not isinstance(block_id, str) or not block_id:
                    raise ValueError(f"invalid block in {pulpo_id}")
                for task in (block.get("tasks") or []):
                    self._add(pulpo_id, block_id, task, None)
                    count += 1
                for family in (block.get("families") or []):
                    family_id = family.get("id")
                    for task in (family.get("tasks") or []):
                        self._add(pulpo_id, block_id, task, family_id)
                        count += 1
            self._counts[pulpo_id] = count

    def _add(self, pulpo: str, block: str, task: dict[str, Any], family: str | None) -> None:
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError(f"invalid task id in {pulpo}/{block}")
        key = (pulpo, block, task_id)
        if key in self._tasks:
            raise ValueError(f"duplicate task in catalog: {key}")
        self._tasks[key] = {**task, "pulpo": pulpo, "block": block, "family": family}

    def get_task(self, pulpo: str, block: str, task_id: str) -> dict[str, Any] | None:
        item = self._tasks.get((pulpo, block, task_id))
        return dict(item) if item else None

    @property
    def task_count(self) -> int:
        return sum(self._counts.values())

    @property
    def pulpo_counts(self) -> dict[str, int]:
        return dict(self._counts)

    def summary(self) -> dict[str, Any]:
        return {"catalog_version": self.version, "task_count": self.task_count,
                "pulpo_counts": self.pulpo_counts}
