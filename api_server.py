"""Authenticated standard-library HTTP API plus local worker loop."""
from __future__ import annotations
import hmac
import json
import logging
import os
import sqlite3
import re
import threading
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote
from core.app import build_runtime, build_planner
from core.catalog import TaskCatalog
from core.task_handlers import build_task_handlers
from connectors.bridge.dispatcher import BridgeDispatcher

MAX_BODY_BYTES = 32_000

def run_worker_loop(runtime, stop_event: threading.Event, interval_seconds: float = 2.0) -> None:
    bridge = BridgeDispatcher(runtime.store)
    while not stop_event.is_set():
        try:
            runtime.run_batch(10)
            bridge.dispatch_pending()
        except Exception as exc:
            # Keep the service alive; do not log task payloads or credentials.
            logging.error("worker_cycle_failed: %s", type(exc).__name__)
        stop_event.wait(interval_seconds)

def build_server(host: str = "127.0.0.1", port: int = 8000,
                 database: str | None = None, api_token: str | None = None,
                 planner=None) -> ThreadingHTTPServer:
    token = api_token if api_token is not None else os.getenv("MULTITAREAS_API_TOKEN", "")
    if not isinstance(token, str) or len(token) < 32:
        raise RuntimeError("MULTITAREAS_API_TOKEN must be configured with at least 32 characters")
    runtime = build_runtime(database)
    central_planner = planner if planner is not None else build_planner()

    class Handler(BaseHTTPRequestHandler):
        server_version = "MultitareasAPI/1.0"

        def log_message(self, _format, *_args):
            # Avoid logging request bodies, tokens or query parameters.
            return

        def _send(self, status: int, body: dict) -> None:
            raw = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)

        def _authorized(self) -> bool:
            supplied = self.headers.get("X-Multitareas-Token", "")
            if not hmac.compare_digest(supplied, self.server.api_token):
                self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
                return False
            return True

        def _read_json(self) -> dict | None:
            content_type = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if content_type != "application/json":
                self._send(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "application_json_required"})
                return None
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_content_length"})
                return None
            if length < 1 or length > MAX_BODY_BYTES:
                self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "request_body_size_invalid"})
                return None
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
                return None
            if not isinstance(body, dict):
                self._send(HTTPStatus.BAD_REQUEST, {"error": "json_object_required"})
                return None
            return body

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/health":
                try:
                    with self.server.runtime.store._connect() as db:
                        check = db.execute("PRAGMA quick_check").fetchone()[0]
                    ok = check == "ok"
                    self._send(HTTPStatus.OK if ok else HTTPStatus.SERVICE_UNAVAILABLE,
                               {"status": "ok" if ok else "degraded",
                                "database": check,
                                "worker_running": bool(self.server.worker_thread and self.server.worker_thread.is_alive())})
                except Exception:
                    self._send(HTTPStatus.SERVICE_UNAVAILABLE, {"status": "degraded", "database": "unavailable"})
                return
            if not self._authorized():
                return
            if path == "/api/coverage":
                catalog = self.server.catalog
                counts = {}
                for pulpo, _block, _task in self.server.handlers:
                    counts[pulpo] = counts.get(pulpo, 0) + 1
                self._send(HTTPStatus.OK, {**catalog.summary(), "handler_counts": counts})
                return
            if path.startswith("/api/tasks/"):
                task_id = unquote(path[len("/api/tasks/"):])
                if not task_id or "/" in task_id:
                    self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_task_id"})
                    return
                item = self.server.runtime.store.get(task_id)
                if item is None:
                    self._send(HTTPStatus.NOT_FOUND, {"error": "task_not_found"})
                    return
                self._send(HTTPStatus.OK, {key: item.get(key) for key in (
                    "task_id", "pulpo", "vertical", "state", "attempts", "max_attempts",
                    "result", "last_error", "created_at", "updated_at")})
                return
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self):
            if not self._authorized():
                return
            path = urlsplit(self.path).path
            body = self._read_json()
            if body is None:
                return
            if path == "/api/tasks":
                pulpo, vertical, payload = body.get("pulpo"), body.get("vertical"), body.get("payload")
                if not isinstance(pulpo, str) or pulpo not in {"ALPHA", "BETA", "GAMMA"} or not isinstance(vertical, str) or not vertical.strip() or not isinstance(payload, dict):
                    self._send(HTTPStatus.BAD_REQUEST, {"error": "pulpo_vertical_and_payload_required"})
                    return
                task_id = body.get("task_id") or str(uuid.uuid4())
                idem = body.get("idempotency_key")
                if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,120}", task_id):
                    self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_task_id"})
                    return
                if idem is not None and (not isinstance(idem, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{8,120}", idem)):
                    self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_idempotency_key"})
                    return
                if len(json.dumps(payload, ensure_ascii=False)) > 16_000:
                    self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "task_payload_too_large"})
                    return
                try:
                    record = self.server.runtime.enqueue(task_id, pulpo, vertical, payload, idem)
                    self._send(HTTPStatus.ACCEPTED, {"task_id": record["task_id"], "state": record["state"]})
                except ValueError as exc:
                    self._send(HTTPStatus.CONFLICT, {"error": str(exc)[:200]})
                except sqlite3.IntegrityError:
                    self._send(HTTPStatus.CONFLICT, {"error": "task_id_conflict"})
                return
            if path == "/api/plans":
                request_context = body.get("request_context")
                allowed = body.get("allowed_pulpos")
                try:
                    plan = self.server.planner.plan(request_context, allowed)
                    self._send(HTTPStatus.OK, plan)
                except PermissionError:
                    self._send(HTTPStatus.FORBIDDEN, {"error": "planner_provider_not_allowed"})
                except RuntimeError:
                    self._send(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "planner_provider_unavailable"})
                except ValueError as exc:
                    self._send(HTTPStatus.BAD_REQUEST, {"error": str(exc)[:200]})
                return
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.api_token = token
    server.runtime = runtime
    server.planner = central_planner
    server.catalog = TaskCatalog()
    server.handlers = build_task_handlers()
    server.worker_thread = None
    return server
