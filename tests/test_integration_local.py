"""Loopback-only end-to-end tests for worker, Cerebro outbox and Multifunction job handoff."""
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from core.store import TaskStore
from connectors.bridge.cerebro import CerebroBridge
from connectors.bridge.dispatcher import BridgeDispatcher
from connectors.bridge.multifuncion import MultifuncionBridge

class LocalBridgeServer:
    def __init__(self):
        self.records = []
        records = self.records
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = json.dumps({"status": "ok"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                records.append({"path": self.path,
                                "headers": {k.lower(): v for k, v in self.headers.items()},
                                "raw": raw, "body": json.loads(raw.decode())})
                body = json.dumps({"accepted": True, "job_id": "local-job-1"}).encode()
                self.send_response(202)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *_args):
                pass
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

class LocalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.http = LocalBridgeServer()
        self.tmp = tempfile.TemporaryDirectory()
        self.store = TaskStore(str(Path(self.tmp.name) / "integration.db"))

    def tearDown(self):
        self.http.close()
        self.tmp.cleanup()

    def test_worker_completion_outbox_and_signed_cerebro_delivery(self):
        self.store.enqueue("task-e2e", "ALPHA", "websites", {"private_brief": "must not leave"})
        self.store.claim()
        self.store.finish("task-e2e", {"state": "NEEDS_ADAPTER"}, "NEEDS_ADAPTER")
        bridge = CerebroBridge(base_url=self.http.base_url, shared_secret="s" * 40,
                               events_path="/events", health_path="/health")
        result = BridgeDispatcher(self.store, bridge).dispatch_pending()
        self.assertEqual(result["sent"], 1)
        self.assertEqual(self.http.records[0]["path"], "/events")
        record = self.http.records[0]
        import hashlib, hmac
        expected = "sha256=" + hmac.new(("s" * 40).encode(), record["raw"], hashlib.sha256).hexdigest()
        self.assertEqual(record["headers"]["x-r3dm-signature"], expected)
        self.assertEqual(record["headers"]["idempotency-key"], record["body"]["event"]["event_id"])
        self.assertNotIn("private_brief", record["raw"].decode())

    @patch.dict(os.environ, {"MULTIFUNCION_BRIDGE_ENABLED": "1"})
    def test_explicit_multifunction_job_handoff_over_loopback(self):
        bridge = MultifuncionBridge(base_url=self.http.base_url, api_token="t" * 40)
        result = bridge.enqueue("BETA", "beta.commission_audit",
                                {"expected_minor": 1200, "received_minor": 1200,
                                 "currency": "EUR"}, "handoff-123456")
        self.assertTrue(result["accepted"])
        record = self.http.records[0]
        self.assertEqual(record["path"], "/api/pulpos/jobs")
        self.assertEqual(record["headers"]["x-pulpo-token"], "t" * 40)
        self.assertEqual(record["headers"]["idempotency-key"], "handoff-123456")
        self.assertEqual(record["body"]["pulpo"], "BETA")

if __name__ == "__main__":
    unittest.main()
