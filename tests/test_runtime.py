import tempfile
import unittest
from pathlib import Path
from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.orchestrator import Orchestrator

class EchoWorker:
    def run(self, task):
        return {"task_id": task.task_id, "state": "SUCCEEDED", "pulpo": task.pulpo}

class UnclearWorker:
    def run(self, task):
        return {"task_id": task.task_id, "state": "PREPARED"}

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

    def test_missing_worker_is_blocked_not_successful(self):
        runtime = WorkerRuntime(self.store, Orchestrator())
        runtime.enqueue("t2", "BETA", "affiliate", {})
        result = runtime.run_once()
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(self.store.get("t2")["state"], "BLOCKED")

    def test_agent_cannot_spend_or_transfer(self):
        for task_id, payload in (("t3", {"spend": True}), ("t4", {"transfer_out": True})):
            self.runtime.enqueue(task_id, "ALPHA", "websites", payload)
            result = self.runtime.run_once()
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"]["reason"], "financial_action_denied")

    def test_agent_cannot_place_investment_order(self):
        self.runtime.enqueue("t5", "GAMMA", "equities",
                             {"requested_action": "investment_order"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"]["reason"], "permission_denied")

    def test_unknown_worker_state_is_not_counted_as_success(self):
        runtime = WorkerRuntime(self.store, Orchestrator({"ALPHA": UnclearWorker()}))
        runtime.enqueue("t6", "ALPHA", "websites", {})
        result = runtime.run_once()
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(self.store.get("t6")["state"], "HUMAN_REVIEW")

if __name__ == "__main__":
    unittest.main()
