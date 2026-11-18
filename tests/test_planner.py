import json
import unittest
from unittest.mock import patch
from core.planner import CentralPlanner

class PlannerTests(unittest.TestCase):
    @patch("core.planner.chat")
    def test_planner_returns_catalog_backed_proposal_only(self, mocked):
        mocked.return_value = json.dumps({
            "summary": "Prepare an opportunity review",
            "tasks": [{"pulpo": "ALPHA", "block": "market_intelligence",
                       "task_key": "score_opportunity",
                       "request_context": "Score supplied opportunity data"}]
        })
        result = CentralPlanner().plan("Assess this supplied opportunity", ["ALPHA"])
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["external_actions_executed"])
        self.assertEqual(result["tasks"][0]["status"], "PROPOSED_NOT_ENQUEUED")

    @patch("core.planner.chat")
    def test_planner_rejects_task_not_in_catalog(self, mocked):
        mocked.return_value = json.dumps({
            "summary": "invalid",
            "tasks": [{"pulpo": "ALPHA", "block": "market_intelligence",
                       "task_key": "invented_task", "request_context": "do something"}]
        })
        with self.assertRaises(ValueError):
            CentralPlanner().plan("Assess an opportunity", ["ALPHA"])

    def test_remote_provider_requires_explicit_opt_in(self):
        with self.assertRaises(PermissionError):
            CentralPlanner(provider="openai")

    def test_context_is_bounded(self):
        with self.assertRaises(ValueError):
            CentralPlanner().plan("x" * 12_001)

if __name__ == "__main__":
    unittest.main()
