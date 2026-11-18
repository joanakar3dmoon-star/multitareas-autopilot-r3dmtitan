import tempfile
import unittest
from pathlib import Path
from core.catalog import TaskCatalog
from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.worker_registry import build_orchestrator

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = WorkerRuntime(TaskStore(str(Path(self.tmp.name) / "catalog.db")),
                                     build_orchestrator())

    def tearDown(self):
        self.tmp.cleanup()

    def test_catalog_has_eighty_one_declared_tasks(self):
        catalog = TaskCatalog()
        self.assertEqual(catalog.task_count, 81)
        self.assertEqual(catalog.pulpo_counts, {"ALPHA": 37, "BETA": 29, "GAMMA": 15})

    def test_registered_handlers_match_catalog_and_pulpo_counts(self):
        from collections import Counter
        from core.task_handlers import build_task_handlers
        catalog = TaskCatalog()
        handlers = build_task_handlers()
        self.assertEqual(len(handlers), 29)
        self.assertEqual(dict(Counter(key[0] for key in handlers)),
                         {"ALPHA": 17, "BETA": 6, "GAMMA": 6})
        for pulpo, block, task_key in handlers:
            self.assertIsNotNone(catalog.get_task(pulpo, block, task_key))

    def test_declared_task_without_handler_is_needs_adapter(self):
        self.runtime.enqueue("alpha-brief-1", "ALPHA", "digital_assets_acquisition",
                             {"block": "digital_assets_acquisition",
                              "task_key": "draft_product_brief",
                              "job_id": "j-1", "request_context": "Draft a digital product brief"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "NEEDS_ADAPTER")
        self.assertEqual(result["outcome"]["reason"], "task_handler_not_registered")

    def test_unknown_catalog_task_is_blocked(self):
        self.runtime.enqueue("unknown-task", "ALPHA", "unknown",
                             {"block": "unknown", "task_key": "invented_task"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"]["reason"], "task_not_in_catalog")

    def test_alpha_record_sources_validates_shape_without_claiming_fetch(self):
        self.runtime.enqueue("alpha-sources", "ALPHA", "market_intelligence",
            {"block": "market_intelligence", "task_key": "record_sources",
             "job_id": "j2", "request_context": "Record sources",
             "source_refs": [{"url": "https://example.org/report", "provider_id": "test",
                              "observed_at": "2026-11-18T05:00:00+00:00"}]})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertFalse(result["outcome"]["result"]["remote_fetch_performed"])

    def test_alpha_opportunity_score_requires_evidence_and_returns_review(self):
        self.runtime.enqueue("alpha-score", "ALPHA", "market_intelligence",
            {"block": "market_intelligence", "task_key": "score_opportunity",
             "job_id": "j3", "request_context": "Rank opportunity",
             "evidence": [{"ref": "source-1"}],
             "validated_records": [{"record_id": "r1", "demand_score": 80,
                                    "evidence_score": 90, "unit_economics_score": 70,
                                    "risk_score": 20}]})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["records"][0]["score"], 80)

    def test_beta_total_price_uses_minor_units(self):
        self.runtime.enqueue("beta-total", "BETA", "merchandising",
            {"block": "merchandising", "task_key": "calculate_total_price",
             "job_id": "j4", "request_context": "Calculate total",
             "product_minor": 1000, "shipping_minor": 250, "tax_minor": 200,
             "fees_minor": 50, "currency": "eur"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertEqual(result["outcome"]["result"]["total_minor"], 1500)

    def test_beta_net_after_reserves_separates_obligations(self):
        self.runtime.enqueue("beta-net", "BETA", "treasury_controls",
            {"block": "treasury_controls", "task_key": "calculate_net_after_reserves",
             "job_id": "j6", "request_context": "Calculate net",
             "confirmed_cash_minor": 100000, "pending_cash_minor": 50000,
             "vat_reserved_minor": 21000, "tax_reserved_minor": 5000,
             "fees_minor": 1000, "refunds_reserved_minor": 2000,
             "committed_costs_minor": 3000, "emergency_reserve_minor": 10000,
             "currency": "EUR"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertEqual(result["outcome"]["result"]["potential_available_minor"], 58000)
        self.assertEqual(result["outcome"]["result"]["pending_cash_excluded_minor"], 50000)

    def test_gamma_available_capital_excludes_pending_and_requires_review(self):
        self.runtime.enqueue("gamma-cash", "GAMMA", "capital_reserves",
            {"block": "capital_reserves", "task_key": "calculate_potential_available_capital",
             "job_id": "j5", "request_context": "Calculate possible capital",
             "confirmed_cash_minor": 100000, "pending_cash_minor": 50000,
             "vat_reserved_minor": 21000, "tax_reserved_minor": 5000,
             "fees_minor": 1000, "refunds_reserved_minor": 2000,
             "committed_costs_minor": 3000, "emergency_reserve_minor": 10000,
             "currency": "EUR"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["potential_available_minor"], 58000)
        self.assertFalse(result["outcome"]["result"]["investment_order_allowed"])

    def test_gamma_separates_pending_and_confirmed_cash(self):
        self.runtime.enqueue("gamma-separate", "GAMMA", "capital_reserves",
            {"block": "capital_reserves", "task_key": "separate_confirmed_and_pending_cash",
             "job_id": "j7", "request_context": "Separate cash",
             "confirmed_cash_minor": 40000, "pending_cash_minor": 9000, "currency": "EUR"})
        result = self.runtime.run_once()
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertFalse(result["outcome"]["result"]["pending_is_available_cash"])

if __name__ == "__main__":
    unittest.main()
