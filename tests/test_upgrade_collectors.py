import tempfile
import unittest
from pathlib import Path
from core.store import TaskStore
from core.runtime import WorkerRuntime
from core.worker_registry import build_orchestrator

class UpgradeCollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = WorkerRuntime(TaskStore(str(Path(self.tmp.name) / "upgrade.db")),
                                     build_orchestrator())
        self.counter = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_task(self, task_key, payload):
        self.counter += 1
        data = {"block": "upgrade_collectors", "task_key": task_key,
                "job_id": f"upgrade-{self.counter}", "request_context": "Validate supplied Upgrade data"}
        data.update(payload)
        self.runtime.enqueue(f"upgrade-{self.counter}", "ALPHA", "upgrade_collectors", data)
        return self.runtime.run_once()

    def test_collect_authorized_quotes_validates_provided_source_refs(self):
        result = self.run_task("collect_authorized_quotes", {
            "source_refs": [{"url": "https://provider.example/quote", "provider_id": "provider-a",
                             "observed_at": "2026-11-18T05:00:00+00:00"}],
            "quotes": [{"provider_id": "provider-a", "bid_minor": 10000, "ask_minor": 10200,
                        "currency": "EUR", "unit": "troy_oz", "observed_at": "2026-11-18T05:00:00+00:00"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["remote_fetch_performed"])

    def test_normalize_currency_unit_uses_explicit_purity_and_weight(self):
        result = self.run_task("normalize_currency_unit", {
            "validated_records": [{"record_id": "q1", "price_minor": 200000,
                                   "unit": "troy_oz", "purity_bps": 9999,
                                   "currency": "EUR", "base_currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        row = result["outcome"]["result"]["normalized_quotes"][0]
        self.assertAlmostEqual(row["pure_weight_grams"], 31.1004, places=4)
        self.assertFalse(row["fx_rate_supplied"])

    def test_calculate_spread_costs_includes_supplied_cost_components(self):
        result = self.run_task("calculate_spread_costs", {
            "validated_records": [{"quote_id": "q1", "bid_minor": 10000, "ask_minor": 10200,
                                   "premium_minor": 100, "fees_minor": 50,
                                   "shipping_minor": 20, "tax_minor": 30, "currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        row = result["outcome"]["result"]["quotes"][0]
        self.assertEqual(row["landed_buy_cost_minor"], 10400)
        self.assertAlmostEqual(row["spread_bps"], 198.02, places=2)

    def test_record_availability_timestamp_does_not_claim_freshness(self):
        result = self.run_task("record_availability_timestamp", {
            "validated_records": [{"provider_id": "p1", "available_quantity": 3,
                                   "observed_at": "2026-11-18T05:00:00+00:00"}]})
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertFalse(result["outcome"]["result"]["availability_records"][0]["freshness_verified"])

    def test_identify_instrument_issuer_is_not_primary_source_verification(self):
        result = self.run_task("identify_instrument_issuer", {
            "instrument_id": "XAU-ETF-1", "issuer": "Example issuer",
            "issuer_id": "LEI-123", "asset_class": "etf"})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["primary_source_verified"])

    def test_review_structure_fees_and_liquidity_against_owner_limits(self):
        result = self.run_task("review_structure_fees_liquidity", {
            "annual_fee_bps": 100, "spread_bps": 200, "liquidity_days": 20,
            "max_annual_fee_bps": 50, "max_spread_bps": 100, "max_liquidity_days": 10})
        self.assertEqual(set(result["outcome"]["result"]["risk_flags"]),
                         {"annual_fee", "spread", "liquidity"})

    def test_record_risks_flags_explicit_components(self):
        result = self.run_task("record_risks", {
            "risk_components": {"issuer": 80, "fx": 30}, "max_risk_score": 50})
        self.assertEqual(result["outcome"]["result"]["risk_flags"], ["issuer"])

    def test_research_suppliers_uses_supplied_records_only(self):
        result = self.run_task("research_suppliers", {
            "suppliers": [{"supplier_id": "s1", "country": "ES",
                           "product_categories": ["gold"], "quoted_price_minor": 10000,
                           "currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["suppliers"][0]["supplier_verified"])

    def test_verify_declared_certifications_does_not_claim_authenticity(self):
        result = self.run_task("verify_declared_certifications", {
            "certifications": [{"certificate_id": "cert-1", "issuer": "Issuer",
                                "valid_until": "2027-12-31", "scope": "gold sourcing"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertFalse(result["outcome"]["result"]["certifications"][0]["authenticity_verified"])

    def test_compare_moq_logistics_and_lead_time_without_order(self):
        result = self.run_task("compare_moq_logistics_lead_times_costs", {
            "required_quantity": 5,
            "supplier_quotes": [{"supplier_id": "s1", "moq": 10, "unit_price_minor": 100,
                                 "shipping_minor": 50, "currency": "EUR", "lead_days": 3}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["supplier_comparison"][0]["total_cost_minor"], 1050)
        self.assertFalse(result["outcome"]["result"]["purchase_order_created"])

    def test_normalize_unit_purity_currency_tax_and_shipping(self):
        result = self.run_task("normalize_unit_purity_currency_tax_shipping", {
            "offers": [{"offer_id": "o1", "weight": 1, "weight_unit": "kg",
                        "purity_bps": 9999, "price_minor": 200000,
                        "tax_minor": 10000, "shipping_minor": 5000,
                        "currency": "EUR", "base_currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        row = result["outcome"]["result"]["normalized_offers"][0]
        self.assertEqual(row["landed_cost_base_minor"], 215000)
        self.assertFalse(row["fx_rate_source_verified"])

    def test_compare_offers_ranks_same_currency_only(self):
        result = self.run_task("compare_offers", {
            "offers": [{"offer_id": "o1", "landed_cost_minor": 12000, "currency": "EUR"},
                       {"offer_id": "o2", "landed_cost_minor": 11000, "currency": "EUR"}]})
        self.assertEqual(result["state"], "HUMAN_REVIEW")
        self.assertEqual(result["outcome"]["result"]["ranked_offers"][0]["offer_id"], "o2")

    def test_record_date_and_evidence_validates_structure_only(self):
        result = self.run_task("record_date_and_evidence", {
            "source_refs": [{"url": "https://provider.example/report", "provider_id": "p1",
                             "observed_at": "2026-11-18T05:00:00+00:00"}],
            "evidence": [{"ref": "report-1"}]})
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertFalse(result["outcome"]["result"]["remote_verification_performed"])

if __name__ == "__main__":
    unittest.main()
