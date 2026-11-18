import tempfile
import unittest
from pathlib import Path

from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.orchestrator import Orchestrator


class EchoWorker:
    def run(self, task):
        return {"task_id": task.task_id, "state": "PREPARED", "pulpo": task.pulpo}


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = TaskStore(str(Path(self.tmp.name) / "tasks.db"))
        self.runtime = WorkerRuntime(self.store, Orchestrator({"ALPHA": EchoWorker()}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_enqueue_claim_and_complete(self):
        self.runtime.enqueue("t1", "ALPHA", "websites", {"brief": "demo"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertEqual(self.store.get("t1")["state"], "SUCCEEDED")
        self.assertEqual([e["event_type"] for e in self.store.audit("t1")],
                         ["TASK_QUEUED", "TASK_CLAIMED", "TASK_SUCCEEDED"])

    def test_idempotency_key_returns_existing_task(self):
        first = self.runtime.enqueue("t1", "ALPHA", "websites", {}, "same-request")
        second = self.runtime.enqueue("t2", "ALPHA", "websites", {"different": True}, "same-request")
        self.assertEqual(first["task_id"], second["task_id"])

    def test_unknown_pulpo_rejected(self):
        with self.assertRaises(ValueError):
            self.runtime.enqueue("t1", "DELTA", "anything", {})

    def test_missing_worker_is_recorded_as_safe_block(self):
        runtime = WorkerRuntime(self.store, Orchestrator())
        runtime.enqueue("t2", "BETA", "affiliate", {})
        result = runtime.run_once()
        self.assertEqual(result["outcome"]["state"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
