"""Composition root for the standalone Multitareas Autopilot runtime."""
import os
from core.runtime import WorkerRuntime
from core.store import TaskStore
from core.worker_registry import build_orchestrator

def build_runtime(database: str | None = None) -> WorkerRuntime:
    """Build the runtime with phase-three workers; external adapters remain gated."""
    store = TaskStore(database or os.getenv("MULTITAREAS_DATABASE", "data/multitareas.db"))
    return WorkerRuntime(store, build_orchestrator())
