import unittest
from core.brain import provider_config
from core.orchestrator import Orchestrator, Task, PULPOS
from core.permissions import AgentPermissions
from pulpos.alpha import AlphaWorker
from pulpos.beta import BetaWorker
from pulpos.gamma import GammaWorker

class ArchitectureTests(unittest.TestCase):
    def test_three_pulpos_only(self):
        self.assertEqual(PULPOS, ("ALPHA", "BETA", "GAMMA"))

    def test_all_pulpos_default_to_review_or_research(self):
        orchestrator = Orchestrator({"ALPHA": AlphaWorker(), "BETA": BetaWorker(), "GAMMA": GammaWorker()})
        for pulpo, vertical, state in (("ALPHA", "dealwork", "HUMAN_REVIEW"), ("BETA", "affiliate", "HUMAN_REVIEW"), ("GAMMA", "equities", "RESEARCH_ONLY")):
            result = orchestrator.dispatch(Task(pulpo, pulpo, vertical, {}))
            self.assertEqual(result["state"], state)

    def test_money_out_is_denied_by_default(self):
        permissions = AgentPermissions()
        for action in ("spend", "transfer_out", "investment_order"):
            with self.assertRaises(PermissionError):
                permissions.require(action)

    def test_provider_selection(self):
        self.assertEqual(provider_config("ollama").name, "ollama")
        with self.assertRaises(ValueError):
            provider_config("unknown-provider")

if __name__ == "__main__":
    unittest.main()
