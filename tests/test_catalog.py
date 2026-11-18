import tempfile
import unittest
from pathlib import Path
from core.catalog import TaskCatalog
from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.worker_registry import build_orchestrator

class CatalogTests(unittest.TestCase):
    def test_catalog_has_eighty_one_declared_tasks(self):
        catalog = TaskCatalog()
        self.assertEqual(catalog.task_count, 81)
        self.assertEqual(catalog.pulpo_counts, {"ALPHA": 37, "BETA": 29, "GAMMA": 15})

    def test_declared_task_without_handler_is_needs_adapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(TaskStore(str(Path(tmp) / "catalog.db")), build_orchestrator())
            runtime.enqueue("alpha-brief-1", "ALPHA", "digital_assets_acquisition",
                            {"block": "digital_assets_acquisition",
                             "task_key": "draft_product_brief",
                             "job_id": "j-1", "request_context": "Draft a digital product brief"})
            result = runtime.run_once()
            self.assertEqual(result["state"], "NEEDS_ADAPTER")
            self.assertEqual(result["outcome"]["reason"], "task_handler_not_registered")

    def test_unknown_catalog_task_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = WorkerRuntime(TaskStore(str(Path(tmp) / "catalog.db")), build_orchestrator())
            runtime.enqueue("unknown-task", "ALPHA", "unknown",
                            {"block": "unknown", "task_key": "invented_task"})
            result = runtime.run_once()
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"]["reason"], "task_not_in_catalog")

if __name__ == "__main__":
    unittest.main()
