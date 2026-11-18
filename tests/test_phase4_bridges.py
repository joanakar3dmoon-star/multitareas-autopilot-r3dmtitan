import hashlib
import hmac
import json
import unittest
from unittest.mock import patch

from integrations.bridge_contracts import build_cerebro_envelope, CONTRACT
from integrations.cerebro_sender import CerebroBridge
from integrations.multifuncion_client import MultifuncionClient

class FakeStore:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.delivered = []
        self.failed = []
    def pending_bridge_events(self, destination, limit):
        assert destination == "cerebro"
        return self.items[:limit]
    def mark_bridge_delivered(self, event_id, destination):
        self.delivered.append((event_id, destination))
    def mark_bridge_failed(self, event_id, destination, error):
        self.failed.append((event_id, destination, error))

def event(payload=None):
    return {"event_id":"123e4567-e89b-12d3-a456-426614174000",
            "event_type":"task.state_changed",
            "payload": payload or {"task_id":"task-7","pulpo":"ALPHA","vertical":"web","state":"SUCCEEDED"},
            "created_at":"2026-11-18T05:00:00+00:00","attempts":0}

class Phase4BridgeTests(unittest.TestCase):
    def test_contract_is_strict_and_privacy_minimal(self):
        envelope = build_cerebro_envelope(event())
        self.assertEqual(envelope["contract"], CONTRACT)
        self.assertEqual(set(envelope["event"]["payload"]), {"task_id","pulpo","vertical","state"})
        with self.assertRaises(ValueError):
            build_cerebro_envelope(event({"task_id":"x","pulpo":"ALPHA","vertical":"web",
                                          "state":"SUCCEEDED","customer_email":"x"}))

    def test_cerebro_bridge_disabled_by_default(self):
        store = FakeStore([event()])
        bridge = CerebroBridge(store, enabled=False)
        self.assertEqual(bridge.deliver_once(), {"enabled":False,"delivered":0,"state":"DISABLED"})
        self.assertEqual(store.delivered, [])

    def test_cerebro_requires_https_and_strong_secret_when_enabled(self):
        with self.assertRaises(ValueError):
            CerebroBridge(FakeStore(), enabled=True, base_url="http://example.com",
                          secret="s"*40)
        with self.assertRaises(ValueError):
            CerebroBridge(FakeStore(), enabled=True, base_url="https://example.com",
                          secret="short")

    def test_cerebro_delivery_hmac_headers_and_ack(self):
        store = FakeStore([event()])
        bridge = CerebroBridge(store, enabled=True, base_url="https://cerebro.example",
                               secret="s"*40)
        captured = {}
        class Response:
            status=200
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def read(self,n): return b'{"accepted":true,"duplicate":false}'
        def fake_urlopen(req, timeout):
            captured["url"]=req.full_url
            captured["headers"]=dict(req.header_items())
            captured["body"]=req.data
            raw_sig=hmac.new(("s"*40).encode(),req.data,hashlib.sha256).hexdigest()
            self_sig=captured["headers"].get("X-r3dm-signature")
            self.assertEqual(self_sig,"sha256="+raw_sig)
            return Response()
        with patch("integrations.cerebro_sender.urllib.request.urlopen", side_effect=fake_urlopen):
            result=bridge.deliver_once()
        self.assertEqual(result["delivered"],1)
        self.assertEqual(store.delivered,[(event()["event_id"],"cerebro")])

    def test_multifuncion_disabled_and_payload_allowlisted(self):
        client=MultifuncionClient(enabled=False)
        self.assertFalse(client.create_job("ALPHA","task",{}, "key")["created"])
        with patch.dict("os.environ", {"MULTIFUNCION_BRIDGE_ENABLED":"1"}):
            client=MultifuncionClient(enabled=True,base_url="https://mf.example",token="t"*40)
            with patch("connectors.bridge.multifuncion.request_json",
                       return_value={"accepted":True,"job_id":"remote-1"}) as mocked:
                result=client.create_job("ALPHA","alpha.intake",{"task_id":"task-1"},
                                         "request-key-123")
            self.assertTrue(result["accepted"])
            self.assertEqual(mocked.call_args.kwargs["headers"]["X-Pulpo-Token"],"t"*40)
            self.assertEqual(mocked.call_args.kwargs["payload"]["worker"],"alpha.intake")
            self.assertEqual(mocked.call_args.kwargs["payload"]["pulpo"],"ALPHA")

    def test_multifuncion_rejects_nested_sensitive_payload_and_requires_flag(self):
        with self.assertRaises(ValueError):
            MultifuncionClient(enabled=True,base_url="https://mf.example",token="t"*40)
        with patch.dict("os.environ", {"MULTIFUNCION_BRIDGE_ENABLED":"1"}):
            client=MultifuncionClient(enabled=True,base_url="https://mf.example",token="t"*40)
            with self.assertRaises(ValueError):
                client.create_job("ALPHA","alpha.intake",
                                  {"input_ref":{"metadata":[{"email":"person@example.com"}]}},
                                  "request-key-123")

    def test_multifuncion_requires_https_and_valid_pulpo(self):
        with patch.dict("os.environ", {"MULTIFUNCION_BRIDGE_ENABLED":"1"}):
            with self.assertRaises(ValueError):
                MultifuncionClient(enabled=True,base_url="http://mf.example",token="t"*40)
            client=MultifuncionClient(enabled=True,base_url="https://mf.example",token="t"*40)
            with self.assertRaises(ValueError):
                client.create_job("DELTA","alpha.intake",{},"request-key-123")

if __name__ == "__main__":
    unittest.main()
