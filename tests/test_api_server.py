import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from api_server import build_server

TOKEN = "multitareas-test-token-" + ("x" * 32)

class FakePlanner:
    def plan(self, request_context, allowed_pulpos=None):
        return {"state": "HUMAN_REVIEW", "summary": request_context,
                "tasks": [], "external_actions_executed": False}

class ApiServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = build_server("127.0.0.1", 0,
            database=str(Path(self.tmp.name) / "api.db"),
            api_token=TOKEN, planner=FakePlanner())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def request(self, path, method="GET", body=None, token=TOKEN):
        headers = {}
        if token:
            headers["X-Multitareas-Token"] = token
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        req = Request(self.base + path, data=data, headers=headers, method=method)
        return urlopen(req, timeout=3)

    def test_health_is_public_and_checks_sqlite(self):
        with self.request("/health") as response:
            body = json.loads(response.read())
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")

    def test_private_routes_require_api_token(self):
        with self.assertRaises(HTTPError) as error:
            self.request("/api/coverage", token="")
        self.assertEqual(error.exception.code, 401)

    def test_task_can_be_submitted_idempotently_and_read_back(self):
        body = {"pulpo": "ALPHA", "vertical": "digital_services",
                "payload": {"brief": "Prepare a service plan"},
                "idempotency_key": "api-request-123456"}
        with self.request("/api/tasks", "POST", body) as response:
            first = json.loads(response.read())
            self.assertEqual(response.status, 202)
        with self.request("/api/tasks", "POST", body) as response:
            second = json.loads(response.read())
        self.assertEqual(first["task_id"], second["task_id"])
        with self.request("/api/tasks/" + first["task_id"]) as response:
            task = json.loads(response.read())
        self.assertEqual(task["state"], "QUEUED")
        self.assertEqual(task["pulpo"], "ALPHA")

    def test_coverage_endpoint_reports_catalog_and_handlers(self):
        with self.request("/api/coverage") as response:
            body = json.loads(response.read())
        self.assertEqual(body["task_count"], 81)
        self.assertEqual(body["handler_counts"], {"ALPHA": 17, "BETA": 6, "GAMMA": 6})

    def test_plan_endpoint_returns_proposal_only(self):
        with self.request("/api/plans", "POST",
                          {"request_context": "Plan a marketplace opportunity",
                           "allowed_pulpos": ["BETA"]}) as response:
            body = json.loads(response.read())
        self.assertEqual(body["state"], "HUMAN_REVIEW")
        self.assertFalse(body["external_actions_executed"])

    def test_api_server_refuses_missing_token(self):
        with self.assertRaises(RuntimeError):
            build_server("127.0.0.1", 0, database=":memory:", api_token="")

if __name__ == "__main__":
    unittest.main()
