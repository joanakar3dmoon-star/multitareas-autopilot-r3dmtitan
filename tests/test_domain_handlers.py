import tempfile
import unittest
from pathlib import Path
from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.worker_registry import build_orchestrator

class DomainHandlerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = WorkerRuntime(TaskStore(str(Path(self.tmp.name) / "domain.db")),
                                     build_orchestrator())
        self.counter = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_task(self, pulpo, block, task_key, payload):
        self.counter += 1
        data = {"block": block, "task_key": task_key,
                "job_id": f"job-{self.counter}", "request_context": "Local deterministic test"}
        data.update(payload)
        self.runtime.enqueue(f"domain-{self.counter}", pulpo, block, data)
        return self.runtime.run_once()

    def test_alpha_identifies_customer_pain_from_supplied_records(self):
        result = self.run_task("ALPHA", "market_intelligence", "identify_customer_pain",
            {"validated_records": [
                {"pain_points": ["slow delivery", "high price"], "evidence_ref": "r1"},
                {"pain_points": ["slow delivery"], "evidence_ref": "r2"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["pain_points"][0]["pain_point"], "slow delivery")
        self.assertFalse(result["outcome"]["result"]["market_representativeness_verified"])

    def test_alpha_compares_declared_affiliate_commissions(self):
        result = self.run_task("ALPHA", "affiliate_operations", "compare_commissions",
            {"programs": [
                {"program_id": "p1", "commission_bps": 1000, "reversal_bps": 100,
                 "cookie_days": 30, "payout_threshold_minor": 5000, "currency": "EUR"},
                {"program_id": "p2", "commission_bps": 800, "reversal_bps": 0,
                 "cookie_days": 60, "payout_threshold_minor": 3000, "currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["provider_terms_fetched"])
        self.assertEqual(result["outcome"]["result"]["programs"][0]["program_id"], "p1")

    def test_beta_normalizes_catalog_without_external_write(self):
        result = self.run_task("BETA", "seller_catalog", "normalize_skus_variants_categories",
            {"items": [{"sku": " ab-123 ", "category": "Home & Garden", "variants": []}]})
        self.assertEqual(result["state"], "SUCCEEDED")
        item = result["outcome"]["result"]["items"][0]
        self.assertEqual(item["sku"], "AB-123")
        self.assertFalse(item["external_catalog_modified"])

    def test_beta_deduplicates_by_reporting_only(self):
        result = self.run_task("BETA", "seller_catalog", "deduplicate_catalog",
            {"items": [{"sku": "a1"}, {"sku": "A1"}, {"sku": "b2"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["duplicate_count"], 1)
        self.assertFalse(result["outcome"]["result"]["records_deleted"])

    def test_beta_validates_price_stock_without_claiming_freshness(self):
        result = self.run_task("BETA", "seller_catalog", "verify_price_stock_currency_timestamp",
            {"items": [{"sku": "a1", "price_minor": 1000, "stock": 2,
                        "currency": "EUR", "observed_at": "2026-11-18T05:00:00+00:00"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["items"][0]["freshness_verified"])

    def test_beta_calculates_margin_and_commission(self):
        result = self.run_task("BETA", "merchandising", "configure_margin_commission_rules",
            {"product_cost_minor": 4000, "sale_price_minor": 10000,
             "commission_bps": 1000, "currency": "EUR"})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["commission_minor"], 1000)
        self.assertEqual(result["outcome"]["result"]["net_contribution_before_tax_minor"], 5000)
        self.assertFalse(result["outcome"]["result"]["price_rule_published"])

    def test_gamma_validates_instrument_identity_without_claiming_verification(self):
        result = self.run_task("GAMMA", "research_analysis", "identify_exact_instrument",
            {"asset_class": "listed_equities", "instrument_id": "ISIN123",
             "issuer": "Example SA", "market": "XETRA", "currency": "EUR"})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["identity_verified_with_primary_source"])

    def test_gamma_risk_flags_use_explicit_limits(self):
        result = self.run_task("GAMMA", "research_analysis",
            "assess_market_issuer_concentration_liquidity_fx_risks",
            {"issuer_concentration_pct": 35, "liquidity_days": 12, "fx_exposure_pct": 15,
             "max_issuer_concentration_pct": 20, "max_liquidity_days": 10,
             "max_fx_exposure_pct": 10})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(set(result["outcome"]["result"]["risk_flags"]),
                         {"issuer_concentration", "liquidity", "fx_exposure"})
        self.assertFalse(result["outcome"]["result"]["investment_order_allowed"])

    def test_gamma_scenarios_are_calculated_from_supplied_assumptions(self):
        result = self.run_task("GAMMA", "research_analysis", "build_adverse_base_favorable_scenarios",
            {"reference_price_minor": 10000, "adverse_change_bps": -2000,
             "base_change_bps": 0, "favorable_change_bps": 1500, "currency": "EUR"})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["scenarios_minor"],
                         {"adverse": 8000, "base": 10000, "favorable": 11500})
        self.assertFalse(result["outcome"]["result"]["forecast_or_prediction"])

    def test_gamma_price_context_calculates_spread_from_supplied_values(self):
        result = self.run_task("GAMMA", "research_analysis", "record_price_currency_liquidity_spread_fees",
            {"price_minor": 10100, "bid_minor": 10000, "ask_minor": 10200,
             "volume": 100, "fee_bps": 5, "currency": "EUR",
             "observed_at": "2026-11-18T05:00:00+00:00"})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["spread_bps"], 198.02)
        self.assertFalse(result["outcome"]["result"]["source_verified"])

if __name__ == "__main__":
    unittest.main()
