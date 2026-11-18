import hashlib
import hmac
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core.store import TaskStore
from connectors.bridge.cerebro import CerebroBridge
from connectors.bridge.dispatcher import BridgeDispatcher
from connectors.bridge.multifuncion import MultifuncionBridge

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = TaskStore(str(Path(self.tmp.name) / "bridge.db"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_cerebro_bridge_requires_explicit_event_path_and_secret(self):
        bridge = CerebroBridge(base_url="https://cerebro.example",
                               shared_secret="s" * 40, events_path="")
        self.assertFalse(bridge.configured)
        self.assertFalse(bridge.handshake()["connected"])

    def test_cerebro_signature_is_hmac_sha256(self):
        secret = "secret" * 8
        body = b'{"event_id":"evt-1"}'
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        self.assertEqual(CerebroBridge.signature(body, secret), expected)

    def test_cerebro_delivery_uses_signed_idempotent_request(self):
        bridge = CerebroBridge(base_url="https://cerebro.example",
                               shared_secret="s" * 40, events_path="/events")
        event = {"event_id": "evt-12345678", "event_type": "task.state_changed",
                 "payload": {"task_id": "t1"}}
        with patch("connectors.bridge.cerebro.request_json", return_value={"accepted": True}) as mocked:
            ok, error = bridge.deliver(event)
        self.assertTrue(ok)
        self.assertIsNone(error)
        headers = mocked.call_args.kwargs["headers"]
        self.assertEqual(headers["Idempotency-Key"], event["event_id"])
        self.assertEqual(headers["X-R3DM-Signature"][:7], "sha256=")

    def test_multifunction_bridge_is_disabled_by_default(self):
        bridge = MultifuncionBridge(base_url="https://multi.example", api_token="t" * 40)
        self.assertFalse(bridge.configured)
        with self.assertRaises(PermissionError):
            bridge.enqueue("ALPHA", "alpha.intake", {}, "request-123456")

    @patch.dict("os.environ", {"MULTIFUNCION_BRIDGE_ENABLED": "1"})
    def test_multifunction_bridge_rejects_sensitive_payload(self):
        bridge = MultifuncionBridge(base_url="https://multi.example", api_token="t" * 40)
        with self.assertRaises(ValueError):
            bridge.enqueue("BETA", "beta.lead", {"email": "person@example.com"}, "request-123456")

    @patch.dict("os.environ", {"MULTIFUNCION_BRIDGE_ENABLED": "1"})
    def test_multifunction_bridge_posts_explicit_job(self):
        bridge = MultifuncionBridge(base_url="https://multi.example", api_token="t" * 40)
        with patch("connectors.bridge.multifuncion.request_json",
                   return_value={"accepted": True, "job_id": "remote-1"}) as mocked:
            result = bridge.enqueue("ALPHA", "alpha.intake",
                                    {"brief": "prepare a digital service"}, "request-123456")
        self.assertTrue(result["accepted"])
        self.assertEqual(mocked.call_args.kwargs["headers"]["X-Pulpo-Token"], "t" * 40)

    def test_task_finish_adds_minimal_event_to_local_outbox(self):
        self.store.enqueue("t1", "ALPHA", "websites", {"brief": "not sent"})
        self.store.claim()
        self.store.finish("t1", {"state": "NEEDS_ADAPTER"}, "NEEDS_ADAPTER")
        pending = self.store.pending_bridge_events("cerebro")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["payload"],
                         {"task_id": "t1", "pulpo": "ALPHA",
                          "vertical": "websites", "state": "NEEDS_ADAPTER"})
        self.assertNotIn("brief", pending[0]["payload"])

    def test_dispatcher_leaves_events_pending_when_not_configured(self):
        self.store.enqueue("t2", "BETA", "affiliate", {})
        self.store.claim()
        self.store.finish("t2", {"state": "NEEDS_ADAPTER"}, "NEEDS_ADAPTER")
        dispatcher = BridgeDispatcher(self.store, CerebroBridge())
        result = dispatcher.dispatch_pending()
        self.assertFalse(result["configured"])
        self.assertEqual(self.store.count_pending_bridge_events(), 1)

    def test_dispatcher_marks_successful_delivery(self):
        self.store.enqueue("t3", "ALPHA", "websites", {})
        self.store.claim()
        self.store.finish("t3", {"state": "NEEDS_ADAPTER"}, "NEEDS_ADAPTER")
        bridge = CerebroBridge(base_url="https://cerebro.example",
                               shared_secret="s" * 40, events_path="/events")
        with patch.object(bridge, "handshake", return_value={"connected": True}), \
             patch.object(bridge, "deliver", return_value=(True, None)):
            result = BridgeDispatcher(self.store, bridge).dispatch_pending()
        self.assertEqual(result["sent"], 1)
        self.assertEqual(self.store.count_pending_bridge_events(), 0)

if __name__ == "__main__":
    unittest.main()
