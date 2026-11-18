import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path
from core.orchestrator import Task
from core.worker_registry import build_orchestrator
from core.app import build_runtime
from connectors.base import ConnectorDisabled
from connectors.marketplaces.adapter import MarketplaceConnector
from connectors.payments.webhook import verify_hmac_sha256, InvalidWebhookSignature
from connectors.payments.ledger import InboundReceiptLedger
from connectors.ai.ollama import OllamaConnector

class PhaseThreeTests(unittest.TestCase):
    def test_registry_runs_alpha_intake_and_plan(self):
        result = build_orchestrator().dispatch(Task("a1", "ALPHA", "websites", {"brief": "Build a site"}))
        self.assertEqual(result["state"], "NEEDS_ADAPTER")
        self.assertIn("steps", result["plan"])

    def test_beta_commission_reconciliation_is_read_only(self):
        result = build_orchestrator().dispatch(Task("b1", "BETA", "affiliate", {"expected_minor": 1000, "received_minor": 900, "currency": "eur"}))
        self.assertEqual(result["commission"]["difference_minor"], -100)
        with self.assertRaises(ValueError):
            build_orchestrator().dispatch(Task("b2", "BETA", "affiliate", {"expected_minor": True, "received_minor": 1, "currency": "EUR"}))

    def test_gamma_research_excludes_crypto_and_never_orders(self):
        result = build_orchestrator().dispatch(Task("g1", "GAMMA", "equities", {"asset_class": "equity", "symbol": "ABC", "price": 10, "observed_at": "2026-11-18T04:00:00+00:00"}))
        self.assertFalse(result["investment_order_allowed"])
        self.assertEqual(result["risk"]["status"], "NOT_EVALUATED")
        self.assertFalse(result["data_quality"]["freshness_checked"])
        with self.assertRaises(ValueError):
            build_orchestrator().dispatch(Task("g2", "GAMMA", "equities", {"asset_class": "crypto"}))

    def test_gamma_risk_requires_explicit_numeric_inputs(self):
        with self.assertRaises(ValueError):
            build_orchestrator().dispatch(Task("g3", "GAMMA", "equities",
                                               {"asset_class": "equity", "risk": {"exposure_pct": True, "limit_pct": 10}}))

    def test_marketplace_connector_fails_closed(self):
        connector = MarketplaceConnector("example")
        self.assertFalse(connector.healthcheck()["enabled"])
        with self.assertRaises(ConnectorDisabled):
            connector.execute()

    def test_ollama_only_allows_local_endpoint(self):
        self.assertEqual(OllamaConnector("http://localhost:11434", "model").name, "ollama")
        with self.assertRaises(ValueError):
            OllamaConnector("https://remote.example", "model")

    def test_webhook_hmac_and_receipt_idempotency(self):
        body, secret = b'{"id":"evt1"}', "test-secret"
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        self.assertTrue(verify_hmac_sha256(body, "sha256=" + signature, secret))
        with self.assertRaises(InvalidWebhookSignature):
            verify_hmac_sha256(body, "sha256=bad", secret)
        with tempfile.TemporaryDirectory() as tmp:
            ledger = InboundReceiptLedger(str(Path(tmp) / "receipts.db"))
            self.assertTrue(ledger.record_verified("test", "evt1", 1250, "eur"))
            self.assertFalse(ledger.record_verified("test", "evt1", 1250, "eur"))
            self.assertEqual(ledger.list_pending()[0]["status"], "PENDING_RECONCILIATION")

    def test_composition_root_uses_phase_three_workers(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = build_runtime(str(Path(tmp) / "runtime.db"))
            runtime.enqueue("app-alpha", "ALPHA", "websites", {"brief": "Create landing page"})
            result = runtime.run_once()
            self.assertEqual(result["state"], "NEEDS_ADAPTER")
            self.assertIn("plan", result["outcome"])

if __name__ == "__main__":
    unittest.main()
