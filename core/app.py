"""Composition root for the standalone Multitareas Autopilot runtime."""
import os
from core.runtime import WorkerRuntime
from core.store import TaskStore
from core.worker_registry import build_orchestrator
from core.planner import CentralPlanner
from core.catalog import TaskCatalog

def build_runtime(database: str | None = None) -> WorkerRuntime:
    """Build the runtime with phase-three workers; external adapters remain gated."""
    store = TaskStore(database or os.getenv("MULTITAREAS_DATABASE", "data/multitareas.db"))
    return WorkerRuntime(store, build_orchestrator())

def build_planner() -> CentralPlanner:
    """Build a catalog-aware planner; local Ollama is the default AI provider."""
    return CentralPlanner(catalog=TaskCatalog(), provider=os.getenv("AI_PROVIDER", "ollama"),
                          allow_remote=os.getenv("AI_REMOTE_ENABLED", "0") == "1")
