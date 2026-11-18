"""Composition root for the standalone Multitareas Autopilot runtime."""
import os
from core.orchestrator import Orchestrator
from core.runtime import WorkerRuntime
from core.store import TaskStore
from pulpos.alpha import AlphaWorker
from pulpos.beta import BetaWorker
from pulpos.gamma import GammaWorker

def build_runtime(database: str | None = None) -> WorkerRuntime:
    """Build the runtime with only local workers; external adapters remain opt-in."""
    store = TaskStore(database or os.getenv("MULTITAREAS_DATABASE", "data/multitareas.db"))
    workers = {"ALPHA": AlphaWorker(), "BETA": BetaWorker(), "GAMMA": GammaWorker()}
    return WorkerRuntime(store, Orchestrator(workers))
