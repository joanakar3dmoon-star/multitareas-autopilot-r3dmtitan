"""Central AI planner: proposes catalog-backed work, never executes external actions."""
from __future__ import annotations
import json
from core.brain import chat
from core.catalog import TaskCatalog

SYSTEM_PROMPT = """You are the planning component of R3DM Multitareas Autopilot.
Return only valid JSON with keys summary and tasks. Each task must contain pulpo, block,
task_key and request_context. Select only tasks from the supplied catalog. Do not invent
sources, prices, leads, customers, stock, payments, revenue or market data. Mark missing
inputs explicitly in request_context. ALPHA plans digital/commercial work and Upgrade
research; BETA plans marketplace operations; GAMMA is research-only for traditional assets.
Never propose crypto, automated trading, purchases, spending, payouts, transfers, refunds,
broker orders, code changes or deployment. This is a proposal only: do not claim anything
was executed or that a sale, payment or investment occurred."""

class CentralPlanner:
    def __init__(self, catalog: TaskCatalog | None = None, provider: str | None = None,
                 allow_remote: bool = False, max_tasks: int = 8):
        if not 1 <= max_tasks <= 10:
            raise ValueError("max_tasks must be between 1 and 10")
        if provider and provider != "ollama" and not allow_remote:
            raise PermissionError("central planner is local-only unless remote use is explicitly enabled")
        self.catalog = catalog or TaskCatalog()
        self.provider = provider
        self.allow_remote = allow_remote
        self.max_tasks = max_tasks

    def plan(self, request_context: str, allowed_pulpos: list[str] | None = None) -> dict:
        if not isinstance(request_context, str) or not request_context.strip():
            raise ValueError("request_context is required")
        if len(request_context) > 12_000:
            raise ValueError("request_context exceeds 12k characters")
        allowed = allowed_pulpos or ["ALPHA", "BETA", "GAMMA"]
        if not allowed or any(p not in {"ALPHA", "BETA", "GAMMA"} for p in allowed):
            raise ValueError("allowed_pulpos must be a non-empty subset of ALPHA/BETA/GAMMA")
        prompt = {
            "request_context": request_context,
            "allowed_pulpos": allowed,
            "catalog": self._catalog_outline(allowed),
            "max_tasks": self.max_tasks,
        }
        raw = chat([{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
                   provider=self.provider, max_tokens=1400)
        try:
            proposal = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("planner returned invalid JSON; no tasks were created") from None
        if not isinstance(proposal, dict) or not isinstance(proposal.get("tasks"), list):
            raise ValueError("planner response must contain a tasks array")
        if len(proposal["tasks"]) > self.max_tasks:
            raise ValueError("planner exceeded max_tasks")
        accepted = []
        for item in proposal["tasks"]:
            if not isinstance(item, dict):
                raise ValueError("each planned task must be an object")
            pulpo, block, task_key = item.get("pulpo"), item.get("block"), item.get("task_key")
            context = item.get("request_context")
            if pulpo not in allowed or not all(isinstance(x, str) and x for x in (block, task_key, context)):
                raise ValueError("planned task has invalid pulpo/block/task_key/request_context")
            spec = self.catalog.get_task(pulpo, block, task_key)
            if spec is None:
                raise ValueError(f"planner proposed task outside catalog: {pulpo}/{block}/{task_key}")
            accepted.append({"pulpo": pulpo, "block": block, "task_key": task_key,
                             "request_context": context[:2000],
                             "approval_required": bool(spec.get("permissions", {}).get("human_approval_required", False)),
                             "status": "PROPOSED_NOT_ENQUEUED"})
        return {"state": "HUMAN_REVIEW", "summary": str(proposal.get("summary", ""))[:1000],
                "tasks": accepted, "external_actions_executed": False,
                "task_catalog_version": self.catalog.version}

    def _catalog_outline(self, allowed: list[str]) -> list[dict]:
        # Expose task identifiers and purpose only, not the full schema.
        result = []
        for pulpo in allowed:
            for (candidate, block, task_key), spec in self.catalog._tasks.items():
                if candidate == pulpo:
                    result.append({"pulpo": candidate, "block": block,
                                   "task_key": task_key, "purpose": spec.get("purpose", "")[:180]})
        return result
